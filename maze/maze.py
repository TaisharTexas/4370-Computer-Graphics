# -*- coding: utf-8 -*-
"""
Project: 3D Maze
Author: Jihao Ye
Start Date: 11/21/2025

Brief Description:
    - Language: Python
    - Stack: pygame, PyOpenGL
"""

# Pylint notes:
# - We intentionally use wildcard imports from pygame.locals and PyOpenGL
#   for convenience in a real-time graphics script.
# - These modules are C extensions / dynamic, so pylint cannot reliably
#   see the symbols and reports them as undefined.
# For THIS file, we disable those specific checks.
# pylint: disable=fixme, wildcard-import, unused-wildcard-import, no-member, undefined-variable, unsupported-binary-operation

import sys
import math
import time
import random

from collections import deque

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


# -----------------------------
# Configuration
# -----------------------------
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# Maze size
MAZE_ROWS = 10
MAZE_COLS = 10
MAZE_CELL_SIZE = 2.0
MAX_SPECIAL_CELLS = 10

FOV_Y = 75.0
NEAR_PLANE = 0.1
FAR_PLANE = 200.0

TARGET_FPS = 60

# Obra Dinn–ish palette
OBRA_LIGHT = (0.9, 0.9, 0.9)  # light tone for walls/floor
OBRA_DARK  = (0.03, 0.03, 0.03)  # background / deep shadows

# -----------------------------
# Texture config
# -----------------------------
TEXTURE_FLOOR_MAIN = "textures/sand_floor_base.jpg"
TEXTURE_WALL = "textures/brick_wall_base.jpg"

def load_texture(path):
    """
    Load an image file as an OpenGL 2D texture and return its texture ID.
    We post-process the image into a 2-tone 'Obra Dinn-ish' palette so
    the texture keeps its pattern but only uses OBRA_LIGHT / OBRA_DARK.
    """
    surface = pygame.image.load(path).convert_alpha()
    tex_data = pygame.image.tostring(surface, "RGBA", True)
    width, height = surface.get_size()

    # --- 2-tone conversion in CPU memory ---
    ba = bytearray(tex_data)

    light_r = int(OBRA_LIGHT[0] * 255)
    light_g = int(OBRA_LIGHT[1] * 255)
    light_b = int(OBRA_LIGHT[2] * 255)

    dark_r = int(OBRA_DARK[0] * 255)
    dark_g = int(OBRA_DARK[1] * 255)
    dark_b = int(OBRA_DARK[2] * 255)

    # Simple luminance threshold
    threshold = 110

    for i in range(0, len(ba), 4):
        r = ba[i]
        g = ba[i + 1]
        b = ba[i + 2]
        # a = ba[i + 3]  # keep alpha as-is

        lum = (r + g + b) // 3

        if lum > threshold:
            ba[i] = light_r
            ba[i + 1] = light_g
            ba[i + 2] = light_b
        else:
            ba[i] = dark_r
            ba[i + 1] = dark_g
            ba[i + 2] = dark_b

    tex_data = bytes(ba)

    # --- Upload to OpenGL ---
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    # Wrap so patterns tile in both directions
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    # Pixel-art look: nearest-neighbor filtering
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        width,
        height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        tex_data,
    )

    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id


# -----------------------------
# Player (movement + orientation)
# -----------------------------
class Player:
    """
    Player holds position and viewing direction
    - position: [x, y]
    - yaw: rotation around Y axis
    - pitch: rotation around x axis
    """

    def __init__(self, start_pos):
        self.position = [start_pos[0], start_pos[1], start_pos[2]]
        self.yaw = 0.0
        self.pitch = 0.0
        self.move_speed = 6.0
        self.mouse_sensitivity = 0.1
        self.vertical_velocity = 0.0
        self.gravity = -20.0
        self.jump_speed = 8.0
        self.ground_y = start_pos[1]

    # ---------- Orientation helpers ----------

    def handle_mouse(self, dx, dy):
        """
        Update yaw/pitch from mouse movement
        """
        self.yaw += dx * self.mouse_sensitivity
        self.pitch -= dy * self.mouse_sensitivity

        # Clamp pitch to avoid flipping over
        self.pitch = max(-89.0, min(89.0, self.pitch))

    def _forward_vector(self):
        """
        Computer the forward direction vector from yaw/pitch
        Return [fx, fy, fz]
        """
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        fx = math.cos(pitch_rad) * math.sin(yaw_rad)
        fy = math.sin(pitch_rad)
        fz = -math.cos(pitch_rad) * math.cos(yaw_rad)

        return [fx, fy, fz]

    def _right_vector(self):
        """
        Computer the right direction vector
        Internal used for WASD movement
        """
        fx, fy, fz = self._forward_vector()
        up = [0.0, 1.0, 0.0]

        # right = forward * up
        rx = fy * up[2] - fz * up[1]
        ry = fz * up[0] - fx * up[2]
        rz = fx * up[1] - fy * up[0]

        length = math.sqrt(rx * rx + ry * ry + rz * rz)
        if length > 0:
            rx /= length
            ry /= length
            rz /= length

        return [rx, ry, rz]

    def handle_keyboard(self, dt, keys):
        """
        Move in the XZ plane based on WASD keys
        """
        dir_x = 0.0
        dir_z = 0.0

        # Froward vector projected onto XZ plane
        fx, _, fz = self._forward_vector()
        length_f = math.sqrt(fx * fx + fz * fz)
        if length_f > 0:
            fx /= length_f
            fz /= length_f

        # Right vector projected onto XZ plane
        rx, _, rz = self._right_vector()
        length_r = math.sqrt(rx * rx + rz * rz)
        if length_r > 0:
            rx /= length_r
            rz /= length_r

        # WASD movement input:
        if keys[K_w]:
            dir_x += fx
            dir_z += fz
        if keys[K_s]:
            dir_x -= fx
            dir_z -= fz
        if keys[K_d]:
            dir_x += rx
            dir_z += rz
        if keys[K_a]:
            dir_x -= rx
            dir_z -= rz

        # Normalize direction
        length_dir = math.sqrt(dir_x * dir_x + dir_z * dir_z)
        if length_dir > 0:
            dir_x /= length_dir
            dir_z /= length_dir

        # Apply movement
        speed = self.move_speed * dt
        self.position[0] += dir_x * speed
        self.position[2] += dir_z * speed

    def update_vertical(self, dt, jump_pressed):
        """
        Apply gravity and optional jump
        - dt: delta time in seconds
        - jump_pressed: bool
        """
        # If on the ground and space is pressed, start a jump
        on_ground = self.position[1] <= self.ground_y + 1e-3
        if jump_pressed and on_ground and self.vertical_velocity <= 0.0:
            self.vertical_velocity = self.jump_speed

        # Gravity always applies
        self.vertical_velocity += self.gravity * dt
        self.position[1] += self.vertical_velocity * dt

        # Clamp to ground
        if self.position[1] < self.ground_y:
            self.position[1] = self.ground_y
            self.vertical_velocity = 0.0

    def set_position(self, x, y, z):
        """
        Teleport the player (used for restart/initalize)
        """
        self.position[0] = x
        self.position[1] = y
        self.position[2] = z

        # Reset vertical state
        self.ground_y = y
        self.vertical_velocity = 0.0

    # ---------- Camera application ----------

    def apply_camera_fps(self):
        """
        Set camera in fps mode (eye at player's head)
        """
        fx, fy, fz = self._forward_vector()
        px, py, pz = self.position

        cx = px + fx
        cy = py + fy
        cz = pz + fz

        glLoadIdentity()
        gluLookAt(px, py, pz,       # eye
                  cx, cy, cz,       # center
                  0.0, 1.0, 0.0)    # up

    def apply_camera_third_p(self):
        """
        Set camera in 3rd-person mode (behind and above the player)
        """
        yaw_rad = math.radians(self.yaw)
        dist = 6.0
        height = 6.0
        px, py, pz = self.position

        eye_x = px - math.sin(yaw_rad) * dist
        eye_y = py + height
        eye_z = pz + math.cos(yaw_rad) * dist

        center_x, center_y, center_z = px, py, pz

        glLoadIdentity()
        gluLookAt(eye_x, eye_y, eye_z,
                  center_x, center_y, center_z,
                  0.0, 1.0, 0.0)

    def apply_camera_top_down(self):
        """
        Set camera in top-down mode (look straight down at player)
        """
        height = 20.0
        px, py, pz = self.position
        eye_x, eye_y, eye_z = px, height, pz
        center_x, center_y, center_z = px, 0.0, pz

        glLoadIdentity()
        gluLookAt(eye_x, eye_y, eye_z,
                  center_x, center_y, center_z,
                  0.0, 0.0, -1.0)

    def apply_camera_overview(self, maze=None):
        """
        Set camera in high view mode (center above the maze)
        """
        if maze is not None:
            cx, cz = maze.get_center_world()
            height = max(30.0, maze.rows * maze.cell_size * 1.5)
            eye_x, eye_y, eye_z = cx, height, cz
            center_x, center_y, center_z = cx, 0.0, cz
        else:
            # Fallback: simple top-down above player
            px, py, pz = self.position
            eye_x, eye_y, eye_z = px, 30.0, pz
            center_x, center_y, center_z = px, 0.0, pz

        glLoadIdentity()
        gluLookAt(eye_x, eye_y, eye_z,
                  center_x, center_y, center_z,
                  0.0, 0.0, -1.0)



# -----------------------------
# Camera controller (view modes)
# -----------------------------
class CameraController:
    """
    CameraController manages different view modes:
        - fps: first-person view from the player's head
        - third_p: 3rd-person view
        - top_down: strict top-down view
        - overview: high view over the max
    """

    def __init__(self):
        self.mode = "fps"


    def apply(self, player, maze=None):
        """
        Sets the view matrix based on current mode
        """
        if self.mode == "fps":
            player.apply_camera_fps()
            return
        elif self.mode == "third_p":
            player.apply_camera_third_p()
            return
        elif self.mode == "top_down":
            player.apply_camera_top_down()
            return
        elif self.mode == "overview":
            player.apply_camera_overview(maze)
            return
        else:
            player.apply_camera_fps()


# -----------------------------
# Maze data structure
# -----------------------------
class Maze:
    """
    Maze holds the logical grid and drawing code
    - rows x cols grid of cells
    - each cell can later store:
        - which walls exist(N/E/S/W)
        - trap / power-up / special type
    """
    def __init__(self, rows, cols, cell_size=2.0):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        # Grid of cells; each cell is a dict for flexibility
        self.grid = [
            [
                {
                    "walls": {"N": True, "E": True, "S": True, "W": True},
                    "type": "empty",
                }
                for _ in range(cols)
            ]
            for _ in range(rows)
        ]

        # Entrance and exit cells
        self.entrance = (0, 0)
        self.exit = (rows - 1, cols - 1)

        # Texture IDs
        self.floor_texture_id = None
        self.wall_texture_id = None

        # Computed after generation
        self.solution_path = []

    # ---------- Coordinate helpers ----------

    def cell_to_world(self, row, col):
        """
        Convert cell (row, col) to world (x, z) center coordinates
        """
        half_w = (self.cols * self.cell_size) / 2.0
        half_h = (self.rows * self.cell_size) / 2.0

        x = (col + 0.5) * self.cell_size - half_w
        z = (row + 0.5) * self.cell_size - half_h

        return x, z

    def get_entrance_world_position(self):
        """
        World-space starting position for thr player at the entrance
        """
        r, c = self.entrance
        x, z = self.cell_to_world(r, c)

        return [x, 1.0, z]

    def get_exit_world_position(self):
        """
        World-space position for the maze exit
        """
        r, c = self.exit
        x, z = self.cell_to_world(r, c)
        return [x, 0.5, z]

    def get_center_world(self):
        """
        World-space center of the maze
        """
        center_row = self.rows / 2.0
        center_col = self.cols / 2.0
        x, z = self.cell_to_world(center_row - 0.5, center_col - 0.5)

        return x, z

    def get_entry_yaw(self):
        """
        Choose a reasonable initial yaw (in degrees) for the player
        at the entrance, based on which neighboring directions are open
        """
        r, c = self.entrance
        cell = self.grid[r][c]

        # South (toward +Z, deeper rows)
        if not cell["walls"]["S"] and r + 1 < self.rows:
            return 180.0
        # East (toward +X, deeper cols)
        if not cell["walls"]["E"] and c + 1 < self.cols:
            return 90.0
        # North (toward -Z)
        if not cell["walls"]["N"] and r - 1 >= 0:
            return 0.0
        # West (toward -X)
        if not cell["walls"]["W"] and c - 1 >= 0:
            return -90.0

        return 0.0

    # ---------- Collision helpers ----------

    def world_to_cell_indices(self, x, z):
        """
        Convert world (x, z) to integer (row, col) indices
        """
        half_w = (self.cols * self.cell_size) / 2.0
        half_h = (self.rows * self.cell_size) / 2.0

        # Shift so (0,0) in grid space is top_left corner of maze
        col = int((x + half_w) // self.cell_size)
        row = int((z + half_h) // self.cell_size)

        return row, col

    def _in_bounds(self, row, col):
        """
        Check if (row, col) is inside the maze grid
        """
        return 0 <= row < self.rows and 0 <= col < self.cols

    def apply_cell_collisions(self, old_x, old_z, new_x, new_z):
        """
        Given an old position and a proposed new position, decide if the move crosses a wall
        - if the move stays in the same cell:
            - aloow movement, but keep a small radius away from any walls in that cell
        - if the move goes to a neighboring cell:
            - check the corresponding wall in the old cell
            - if there is a wall, block (return old position)
            - if no wall, allow (return new position)
        - If the move goes outside the maze or jumps over more than one cell: block
        """
        row0, col0 = self.world_to_cell_indices(old_x, old_z)
        row1, col1 = self.world_to_cell_indices(new_x, new_z)

        if not (self._in_bounds(row0, col0) and self._in_bounds(row1, col1)):
            return old_x, old_z

        # Same cell => stay inside, but keep a small radius away from walls
        if row0 == row1 and col0 == col1:
            cell = self.grid[row0][col0]

            x_center, z_center = self.cell_to_world(row0, col0)
            s = self.cell_size / 2.0

            x_left  = x_center - s
            x_right = x_center + s
            z_top   = z_center - s
            z_bottom = z_center + s

            # Player radius: how close we allow to get to a wall
            radius = self.cell_size * 0.1

            x_clamped = new_x
            z_clamped = new_z

            # Keep away from north wall
            if cell["walls"]["N"]:
                min_z = z_top + radius
                if z_clamped < min_z:
                    z_clamped = min_z
            # Keep away from south wall
            if cell["walls"]["S"]:
                max_z = z_bottom - radius
                if z_clamped > max_z:
                    z_clamped = max_z
            # Keep away from west wall
            if cell["walls"]["W"]:
                min_x = x_left + radius
                if x_clamped < min_x:
                    x_clamped = min_x
            # Keep away from east wall
            if cell["walls"]["E"]:
                max_x = x_right - radius
                if x_clamped > max_x:
                    x_clamped = max_x

            return x_clamped, z_clamped

        dr = row1 - row0
        dc = col1 - col0

        if abs(dr) + abs(dc) > 1:
            return old_x, old_z

        cell = self.grid[row0][col0]

        # Moving north
        if dr == -1 and dc == 0:
            if cell["walls"]["N"]:
                return old_x, old_z
            else:
                return new_x, new_z
        # Moving south
        if dr == 1 and dc == 0:
            if cell["walls"]["S"]:
                return old_x, old_z
            else:
                return new_x, new_z
        # Moving east
        if dr == 0 and dc == 1:
            if cell["walls"]["E"]:
                return old_x, old_z
            else:
                return new_x, new_z
        # Moving west
        if dr == 0 and dc == -1:
            if cell["walls"]["W"]:
                return old_x, old_z
            else:
                return new_x, new_z

        return new_x, new_z

    # ---------- Generation (TODO) ----------

    def generate_random(self, seed=None):
        """
        Generate a random maze using a depth-first search (DFS) backtracker.
        - start from the entrance cell
        - removes walls between cells to form a spanning tree
        """
        # Local RNG so seeding does not affect global random state
        rng = random.Random(seed)

        # Reset all walls to present and types to empty
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                cell["walls"] = {"N": True, "E": True, "S": True, "W": True}
                cell["type"] = "empty"

        # Visited grid for DFS
        visited = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        # Start from entrance
        start_r, start_c = self.entrance
        self._carve_passages_from(start_r, start_c, visited, rng)

        # Exit is currently fixed at bottom-right; DFS guarantees it's reachable.
        # Later, we can optionally choose exit as farthest cell from entrance.
        self._assign_special_cells(rng)

    def _carve_passages_from(self, r, c, visited, rng):
        """
        Recursive DFS maze carver
        - r, c: current cell indices
        - visited: 2D list of booleans
        - rng: random.Random instance
        """
        visited[r][c] = True

        # Directions: (dir_key, dr, dc, opposite_dir_key)
        directions = [
            ("N", -1, 0, "S"),
            ("S", 1, 0, "N"),
            ("W", 0, -1, "E"),
            ("E", 0, 1, "W"),
        ]
        rng.shuffle(directions)

        for dir_key, dr, dc, opposite_key in directions:
            nr = r + dr
            nc = c + dc

            # Check bounds
            if nr < 0 or nr >= self.rows or nc < 0 or nc >= self.cols:
                continue

            if not visited[nr][nc]:
                self.grid[r][c]["walls"][dir_key] = False
                self.grid[nr][nc]["walls"][opposite_key] = False

                # Recurse into neighbor
                self._carve_passages_from(nr, nc, visited, rng)

    def _compute_solution_path(self):
            """
            Compute a path from entrance to exit using BFS on the carved maze
            """
            start = self.entrance
            goal = self.exit

            queue = deque([start])
            parents = {start: None}

            while queue:
                r, c = queue.popleft()
                if (r, c) == goal:
                    break

                cell = self.grid[r][c]
                neighbors = []
                if not cell["walls"]["N"]:
                    neighbors.append((r - 1, c))
                if not cell["walls"]["S"]:
                    neighbors.append((r + 1, c))
                if not cell["walls"]["W"]:
                    neighbors.append((r, c - 1))
                if not cell["walls"]["E"]:
                    neighbors.append((r, c + 1))

                for nr, nc in neighbors:
                    if (nr, nc) not in parents:
                        parents[(nr, nc)] = (r, c)
                        queue.append((nr, nc))

            # Reconstruct path
            if goal not in parents:
                return []

            path = []
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = parents[cur]
            path.reverse()
            return path

    def _assign_special_cells(self, rng):
        """
        Assign cell['type'] values for traps / power-ups:
        - 'entrance', 'exit'
        - 'speed'  : speed boost on main path
        - 'launch' : launch upward for overview
        - 'slow'   : slow cells off the main path
        - 'reset'  : send player back to start
        - 'turn'   : rotate player 90 degrees
        """
        # Start by clearing types
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c]["type"] = "empty"

        # Compute main path
        self.solution_path = self._compute_solution_path()

        # Mark entrance/exit
        er, ec = self.entrance
        xr, xc = self.exit
        self.grid[er][ec]["type"] = "entrance"
        self.grid[xr][xc]["type"] = "exit"

        max_special = MAX_SPECIAL_CELLS
        total_special = 0

        # Inner path (exclude endpoints)
        path_inner = [
            cell for cell in self.solution_path
            if cell not in (self.entrance, self.exit)
        ]
        rng.shuffle(path_inner)

        # Speed boost cells along main path
        num_speed = min(2, max(1, len(path_inner) // 8))
        for r, c in path_inner[:num_speed]:
            if total_special >= max_special:
                break
            self.grid[r][c]["type"] = "speed"
            total_special += 1

        # One launch cell on the main path if possible
        if total_special < max_special and len(path_inner) > num_speed:
            lr, lc = path_inner[num_speed]
            self.grid[lr][lc]["type"] = "launch"
            total_special += 1

        # Collect dead ends
        dead_ends = []
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in (self.entrance, self.exit):
                    continue
                cell = self.grid[r][c]
                openings = 0
                if not cell["walls"]["N"]:
                    openings += 1
                if not cell["walls"]["S"]:
                    openings += 1
                if not cell["walls"]["E"]:
                    openings += 1
                if not cell["walls"]["W"]:
                    openings += 1
                if openings == 1:
                    dead_ends.append((r, c))

        rng.shuffle(dead_ends)
        available = max_special - total_special
        num_reset = min(2, len(dead_ends), available)
        for r, c in dead_ends[:num_reset]:
            self.grid[r][c]["type"] = "reset"
            total_special += 1

        # Slow cells off the main path
        off_path_cells = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if (r, c) not in self.solution_path
            and self.grid[r][c]["type"] == "empty"
        ]
        rng.shuffle(off_path_cells)
        available = max_special - total_special
        num_slow = min(3, len(off_path_cells), available)
        for r, c in off_path_cells[:num_slow]:
            self.grid[r][c]["type"] = "slow"
            total_special += 1

        # Turn-90 cells anywhere that is still empty
        remaining = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if self.grid[r][c]["type"] == "empty"
        ]
        rng.shuffle(remaining)
        available = max_special - total_special
        num_turn = min(3, len(remaining), available)
        for r, c in remaining[:num_turn]:
            self.grid[r][c]["type"] = "turn"
            total_special += 1

    # ---------- Drawing ----------

    def draw(self):
        """
        Draw floor for each cell and walls around the maze
        - draw individual walls according to self.grid[r][c]["walls"]
        - apply textures and lighting
        - add visual markers for traps/power-ups
        - uses textures if floor_texture_id / wall_texture_id are set.
        """
        # ----- Floor -----
        if self.floor_texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.floor_texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        # Slightly darker than walls for readability.
        glColor3f(
            OBRA_LIGHT[0] * 0.5,
            OBRA_LIGHT[1] * 0.5,
            OBRA_LIGHT[2] * 0.5,
        )
        for r in range(self.rows):
            for c in range(self.cols):
                self._draw_floor_cell(r, c)

        # Unbind floor texture
        if self.floor_texture_id is not None:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

        # ----- Walls -----
        if self.wall_texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.wall_texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        # Base wall color – light tone
        glColor3f(OBRA_LIGHT[0], OBRA_LIGHT[1], OBRA_LIGHT[2])
        self._draw_all_walls()

        if self.wall_texture_id is not None:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)

    def _draw_floor_cell(self, row, col):
        """
        Draw a single floor quad for cell (row, col)
        """
        x_center, z_center = self.cell_to_world(row, col)
        s = self.cell_size / 2.0

        x0 = x_center - s
        x1 = x_center + s
        z0 = z_center - s
        z1 = z_center + s

        glNormal3f(0.0, 1.0, 0.0)  # floor points straight up

        glBegin(GL_QUADS)
        # Simple 0..1 UV across the cell
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x0, 0.0, z0)

        glTexCoord2f(1.0, 0.0)
        glVertex3f(x1, 0.0, z0)

        glTexCoord2f(1.0, 1.0)
        glVertex3f(x1, 0.0, z1)

        glTexCoord2f(0.0, 1.0)
        glVertex3f(x0, 0.0, z1)
        glEnd()

    def _draw_all_walls(self):
        """
        Draw walls for each cell according to its 'walls' dictionary
        To avoid drawing shared walls twice:
        - for every cell, draw N and W walls if present
        - for the last row, also draw S walls
        - for the last column, also draw E walls
        """
        wall_height = 2.0

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                x_center, z_center = self.cell_to_world(r, c)
                s = self.cell_size / 2.0

                # Precompute cell edge coordinates
                x_left = x_center - s
                x_right = x_center + s
                z_top = z_center - s
                z_bottom = z_center + s

                # North wall
                if cell["walls"]["N"]:
                    self._draw_wall_segment(x_left, z_top, x_right, z_top, wall_height)
                # West wall
                if cell["walls"]["W"]:
                    self._draw_wall_segment(x_left, z_top, x_left, z_bottom, wall_height)
                # South wall
                if r == self.rows - 1 and cell["walls"]["S"]:
                    self._draw_wall_segment(x_left, z_bottom, x_right, z_bottom, wall_height)
                # East wall
                if c == self.cols - 1 and cell["walls"]["E"]:
                    self._draw_wall_segment(x_right, z_top, x_right, z_bottom, wall_height)

    def _draw_wall_segment(self, x0, z0, x1, z1, height):
        """
        Draw a vertical wall quad along the segment from (x0, z0) to (x1, z1)
        with a simple 0..1 UV mapping.
        """
        # Compute a horizontal normal for this wall
        dx = x1 - x0
        dz = z1 - z0
        length = math.sqrt(dx * dx + dz * dz) or 1.0
        # Perpendicular vector in XZ plane
        nx = -dz / length
        nz = dx / length

        glBegin(GL_QUADS)
        glNormal3f(nx, 0.0, nz)
        # Bottom edge
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x0, 0.0, z0)

        glTexCoord2f(1.0, 0.0)
        glVertex3f(x1, 0.0, z1)

        # Top edge
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x1, height, z1)

        glTexCoord2f(0.0, 1.0)
        glVertex3f(x0, height, z0)
        glEnd()

# -----------------------------
# Game (main loop + glue)
# -----------------------------
class Game:
    """
    Game ties together:
        - Window + OpenGL setup
        - Player, CameraController, Maze
        - Event handling, update, render loop
    """

    def __init__(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT):
        pygame.init()
        pygame.display.set_caption("3D Maze Game - Jihao Ye")

        self.font = pygame.font.SysFont("consolas", 20)

        flags = DOUBLEBUF | OPENGL  # pylint: disable=unsupported-binary-operation
        pygame.display.set_mode((width, height), flags)
        self.width = width
        self.height = height
        self.running = True

        # OpenGL setup
        self.init_opengl()

        # Textures
        self.tex_floor_main = load_texture(TEXTURE_FLOOR_MAIN)
        self.tex_wall = load_texture(TEXTURE_WALL)

        # Maze
        self.maze = Maze(MAZE_ROWS, MAZE_COLS, MAZE_CELL_SIZE)
        self.maze.floor_texture_id = self.tex_floor_main
        self.maze.wall_texture_id = self.tex_wall
        self.maze.generate_random(seed=None) # TODO: replace placeholder

        # Player
        start_pos = self.maze.get_entrance_world_position()
        self.player = Player(start_pos)
        self.player.yaw = self.maze.get_entry_yaw()
        self.player.pitch = 0.0

        # Movement baseline and current cell
        self.base_move_speed = self.player.move_speed
        row0, col0 = self.maze.world_to_cell_indices(
            self.player.position[0],
            self.player.position[2],
        )
        self.current_cell = (row0, col0)

        # Camera
        self.camera = CameraController()

        # Mouse grab
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        # Timing
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.elapsed_time = 0.0

        # Game state
        self.game_state = "playing"
        self.final_time = 0.0

        # Hint system
        self.max_hints = 3
        self.hints_used = 0
        self.hint_active = False
        self.hint_duration = 4.0
        self.hint_cooldown = 10.0
        self.hint_next_available_time = 0.0
        self.hint_end_time = 0.0
        self.hint_cells = []
        self.hint_request = False

    def init_opengl(self):
        """
        Configure basic OpenGL state.
        """
        glViewport(0, 0, self.width, self.height)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV_Y, self.width / float(self.height), NEAR_PLANE, FAR_PLANE)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Lighting setup
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)

        global_ambient = (0.18, 0.18, 0.18, 1.0)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_ambient)

        # Light above the maze, pointing down
        light_pos = (0.0, 20.0, 0.0, 1.0)
        light_ambient = (0.25, 0.25, 0.25, 1.0)
        light_diffuse = (1.0, 1.0, 1.0, 1.0)

        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)

        # Simple fog that fades into the dark background
        glEnable(GL_FOG)
        fog_color = (OBRA_DARK[0], OBRA_DARK[1], OBRA_DARK[2], 1.0)
        glFogfv(GL_FOG_COLOR, fog_color)
        glFogi(GL_FOG_MODE, GL_LINEAR)

        maze_extent = MAZE_ROWS * MAZE_CELL_SIZE
        glFogf(GL_FOG_START, maze_extent * 0.5)
        glFogf(GL_FOG_END,   maze_extent * 1.5)

        # Let glColor* control material color
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        glShadeModel(GL_FLAT)

        # Projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(FOV_Y, self.width / float(self.height), NEAR_PLANE, FAR_PLANE)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)

    def handle_events(self):
        """
        Handle pygame events and return mouse deltas.
        """
        mouse_dx, mouse_dy = 0, 0

        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False

                # Camera mode switching
                elif event.key == K_1:
                    self.camera.mode = "fps"
                    print("Camera mode: fps")
                elif event.key == K_2:
                    self.camera.mode = "third_p"
                    print("Camera mode: third-person")
                elif event.key == K_3:
                    self.camera.mode = "top_down"
                    print("Camera mode: top-down")
                elif event.key == K_4:
                    self.camera.mode = "overview"
                    print("Camera mode: overview")

                # Restart from entrance
                elif event.key == K_r:
                    self.restart_from_entrance()
                    print("Restarted from entrance")

                # Regenerate maze
                elif event.key == K_n:
                    self.regenerate_maze()
                    print("Regenerated maze")

                # Request hint
                elif event.key == K_h:
                    self.hint_request = True

            elif event.type == MOUSEMOTION:
                dx, dy = event.rel
                mouse_dx += dx
                mouse_dy += dy

        return mouse_dx, mouse_dy

    def restart_from_entrance(self):
        """
        Reset player to entrance and reset timer.
        """
        start_pos = self.maze.get_entrance_world_position()
        self.player.set_position(*start_pos)
        self.player.yaw = self.maze.get_entry_yaw()
        self.player.pitch = 0.0
        row0, col0 = self.maze.world_to_cell_indices(
            self.player.position[0],
            self.player.position[2],
        )
        self.current_cell = (row0, col0)
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.game_state = "playing"
        self.final_time = 0.0
        # Reset hints
        self.hints_used = 0
        self.hint_active = False
        self.hint_cells = []
        self.hint_next_available_time = 0.0
        self.hint_end_time = 0.0
        self.hint_request = False

    def regenerate_maze(self):
        """
        Create a new maze, move player to entrance, reset timer.
        """
        self.maze.generate_random(seed=None)
        start_pos = self.maze.get_entrance_world_position()
        self.player.set_position(*start_pos)
        self.player.yaw = self.maze.get_entry_yaw()
        self.player.pitch = 0.0
        row0, col0 = self.maze.world_to_cell_indices(
            self.player.position[0],
            self.player.position[2],
        )
        self.current_cell = (row0, col0)
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.game_state = "playing"
        self.final_time = 0.0
        # Reset hints
        self.hints_used = 0
        self.hint_active = False
        self.hint_cells = []
        self.hint_next_available_time = 0.0
        self.hint_end_time = 0.0
        self.hint_request = False

    def _maybe_activate_hint(self, row, col):
        """
        Try to activate a path hint near the given cell (row, col).
        Respects max_hints and cooldown.
        """
        # No hints left
        if self.hints_used >= self.max_hints:
            return

        # Still on cooldown
        if self.elapsed_time < self.hint_next_available_time:
            return

        path = self.maze.solution_path
        if not path:
            return

        # Find index of current cell on the solution path, or nearest path cell
        try:
            idx = path.index((row, col))
        except ValueError:
            idx = min(
                range(len(path)),
                key=lambda i: abs(path[i][0] - row) + abs(path[i][1] - col),
            )

        # Show a small segment of the path ahead from this index
        segment_len = 5
        start_idx = idx
        end_idx = min(len(path), idx + segment_len)
        self.hint_cells = path[start_idx:end_idx]

        # Activate hint
        self.hint_active = True
        self.hint_end_time = self.elapsed_time + self.hint_duration
        self.hint_next_available_time = self.elapsed_time + self.hint_cooldown
        self.hints_used += 1

    def update(self, dt, mouse_dx, mouse_dy):
        """
        Update game state: orientation, movement, timer.
        """
        # If already won, keep state frozen
        if self.game_state != "playing":
            return

        # Mouse -> orientation
        self.player.handle_mouse(mouse_dx, mouse_dy)

        # Keyboard -> movement
        keys = pygame.key.get_pressed()
        old_x = self.player.position[0]
        old_z = self.player.position[2]
        self.player.handle_keyboard(dt, keys)
        desired_x = self.player.position[0]
        desired_z = self.player.position[2]

        mid_x, mid_z = self.maze.apply_cell_collisions(old_x, old_z, desired_x, old_z)
        final_x, final_z = self.maze.apply_cell_collisions(mid_x, mid_z, mid_x, desired_z)

        self.player.position[0] = final_x
        self.player.position[2] = final_z

        self.player.update_vertical(dt, keys[K_SPACE])

        # Which cell are we in now
        new_row, new_col = self.maze.world_to_cell_indices(
            self.player.position[0],
            self.player.position[2],
        )
        entered_new = (new_row, new_col) != self.current_cell
        if entered_new:
            self.current_cell = (new_row, new_col)

        # Apply cell-based effects
        self._apply_cell_effect(new_row, new_col, entered_new)


        # Timer
        self.elapsed_time = time.time() - self.start_time

        # Expire active hint when time is up
        if self.hint_active and self.elapsed_time >= self.hint_end_time:
            self.hint_active = False
            self.hint_cells = []

        # If player pressed H this frame, try to activate a hint
        if self.hint_request and self.game_state == "playing":
            self._maybe_activate_hint(self.current_cell[0], self.current_cell[1])
            self.hint_request = False

        # Check if reached exit
        if self._player_at_exit():
            self.game_state = "won"
            self.final_time = self.elapsed_time

    def _player_at_exit(self):
        """
        Return True if the player's cell matches the maze exit cell
        """
        px = self.player.position[0]
        pz = self.player.position[2]
        row, col = self.maze.world_to_cell_indices(px, pz)
        exit_r, exit_c = self.maze.exit
        return row == exit_r and col == exit_c

    def _start_2d(self):
        """
        Switch to 2D orthographic projection for HUD drawing
        """
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

    def _end_2d(self):
        """
        Restore 3D projection/modelview after HUD drawing.
        """
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glEnable(GL_LIGHTING)
        glMatrixMode(GL_MODELVIEW)

    def draw_scene(self):
        """
        Render the 3D world and HUD.
        """
        glClearColor(OBRA_DARK[0], OBRA_DARK[1], OBRA_DARK[2], 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set camera
        self.camera.apply(self.player, self.maze)

        # Light above maze center (world-space)
        cx, cz = self.maze.get_center_world()
        light_pos = (cx, 20.0, cz, 1.0)
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

        # Draw maze (floor + border walls)
        self.maze.draw()

        # Visual markers for traps / power-ups
        self._draw_special_markers()

        # Hint overlay on solution path
        self._draw_hint_overlay()

        # Draw player marker in non-FPS camera modes
        if self.camera.mode != "fps":
            self._draw_player_marker()

        # Mark exit cell with a green cube
        ex, _, ez = self.maze.get_exit_world_position()
        glColor3f(0.2, 0.8, 0.3)
        self._draw_unit_cube_at(ex, 0.5, ez)

        # 2D HUD
        self.draw_hud()

        # TODO:
        # - draw player model for third-person/top-down

    def _draw_unit_cube_at(self, x, y, z, scale=None):
        """
        Draw a cube centered at (x, y, z).
        If 'scale' is provided as (sx, sy, sz), scale the cube accordingly.
        """
        s = 0.5
        vertices = [
            [-s, -s, -s],
            [s, -s, -s],
            [s, s, -s],
            [-s, s, -s],
            [-s, -s, s],
            [s, -s, s],
            [s, s, s],
            [-s, s, s],
        ]
        # (indices, normal)
        faces = [
            ([0, 1, 2, 3],  (0.0, 0.0, -1.0)),  # front
            ([3, 2, 6, 7],  (0.0, 1.0, 0.0)),  # top
            ([7, 6, 5, 4],  (0.0, 0.0, 1.0)),  # back
            ([4, 5, 1, 0],  (0.0, -1.0, 0.0)),  # bottom
            ([1, 5, 6, 2],  (1.0, 0.0, 0.0)),  # right
            ([4, 0, 3, 7],  (-1.0, 0.0, 0.0)),  # left
        ]

        glPushMatrix()
        glTranslatef(x, y, z)
        if scale is not None:
            glScalef(scale[0], scale[1], scale[2])

        glBegin(GL_QUADS)
        for face, normal in faces:
            glNormal3f(*normal)
            for idx in face:
                glVertex3fv(vertices[idx])
        glEnd()
        glPopMatrix()

    def _draw_player_marker(self):
        """
        Draw a simple marker representing the player's body.
        Only used for non-FPS camera modes.
        """
        px, py, pz = self.player.position

        center_y = 0.6
        marker_scale = (0.3, 1.0, 0.3)

        glColor3f(1.0, 0.9, 0.3)
        self._draw_unit_cube_at(px, center_y, pz, scale=marker_scale)

    def _draw_special_markers(self):
        """
        Draw small colored cubes on cells with special types so the player
        can visually recognize traps / power-ups.
        """
        tile_scale = (0.9, 0.04, 0.9)
        sx, sy, sz = tile_scale

        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)

        for r in range(self.maze.rows):
            for c in range(self.maze.cols):
                ctype = self.maze.grid[r][c]["type"]
                if ctype not in ("speed", "slow", "reset", "turn", "launch"):
                    continue

                x, z = self.maze.cell_to_world(r, c)
                y = sy * 0.5

                if ctype == "speed":
                    glColor3f(0.2, 1.0, 1.0)      # cyan
                elif ctype == "slow":
                    glColor3f(0.6, 0.2, 0.9)      # purple
                elif ctype == "reset":
                    glColor3f(1.0, 0.2, 0.2)      # red
                elif ctype == "turn":
                    glColor3f(1.0, 1.0, 0.2)      # yellow
                elif ctype == "launch":
                    glColor3f(1.0, 1.0, 1.0)      # white

                self._draw_unit_cube_at(x, y, z, scale=tile_scale)

        glEnable(GL_LIGHTING)

    def _draw_hint_overlay(self):
        """
        Draw thin green tiles on the solution path when a hint is active.
        """
        if not self.hint_active or not self.hint_cells:
            return

        # Thin tile that almost fills the cell
        tile_scale = (0.9, 0.04, 0.9)
        sx, sy, sz = tile_scale

        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glColor3f(0.3, 0.3, 0.3)

        for r, c in self.hint_cells:
            x, z = self.maze.cell_to_world(r, c)
            y = sy * 0.5 + 0.001
            self._draw_unit_cube_at(x, y, z, scale=tile_scale)

        glEnable(GL_LIGHTING)

    def _draw_text_2d(self, x, y, text, color=(255, 255, 255, 255)):
        """
        Draw text at screen coordinates (x, y) using a temporary texture.
        (0,0) is top-left of the window.
        """
        if not text:
            return

        # Render text to a pygame surface
        surface = self.font.render(text, True, color[:3])
        text_data = pygame.image.tostring(surface, "RGBA", False)
        w, h = surface.get_size()

        # Create a temporary texture
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Draw textured quad
        glColor4f(1.0, 1.0, 1.0, 1.0)

        # Draw textured quad
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(x, y)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(x + w, y)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(x + w, y + h)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(x, y + h)
        glEnd()

        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        glDeleteTextures([tex_id])

    def draw_hud(self):
        """
        Draw HUD with elapsed time and player position (cell indices).
        """
        # Choose which time to display
        if self.game_state == "won":
            display_time = self.final_time
        else:
            display_time = self.elapsed_time

        # Format time as MM:SS
        total_seconds = int(display_time)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        time_text = f"Time: {minutes:02d}:{seconds:02d}"

        # Player cell position
        px = self.player.position[0]
        pz = self.player.position[2]
        row, col = self.maze.world_to_cell_indices(px, pz)
        pos_text = f"Cell: ({row}, {col})"

        # Optional: world coords (rounded)
        world_text = f"Pos: ({px:.1f}, {pz:.1f})"

        # Current cell type
        cell_type = "unknown"
        if 0 <= row < self.maze.rows and 0 <= col < self.maze.cols:
            cell_type = self.maze.grid[row][col].get("type", "empty")

        type_labels = {
            "empty": "Empty",
            "entrance": "Entrance",
            "exit": "Exit",
            "speed": "Speed boost",
            "slow": "Slow zone",
            "reset": "Reset trap",
            "turn": "Turn tile",
            "launch": "Launch pad",
        }
        type_text = f"Tile: {type_labels.get(cell_type, cell_type)}"

        # Status / hint text
        if self.game_state == "won":
            status_text = "Reached EXIT! Press R to restart, N for new maze."
        else:
            exit_r, exit_c = self.maze.exit
            status_text = (
                f"Exit cell: ({exit_r}, {exit_c}) | "
                "R: restart | N: new maze | 1-4: camera"
            )

        # Hint status
        if self.hints_used >= self.max_hints:
            hint_text = "Hints: 0 left"
        else:
            remaining = self.max_hints - self.hints_used
            if self.elapsed_time < self.hint_next_available_time:
                cd = int(self.hint_next_available_time - self.elapsed_time) + 1
                hint_text = f"Hints: {remaining} (H on cooldown: {cd}s)"
            else:
                hint_text = f"Hints: {remaining} (press H for a path hint)"

        self._start_2d()
        # Top-left corner
        self._draw_text_2d(10, 10, time_text)
        self._draw_text_2d(10, 35, pos_text)
        self._draw_text_2d(10, 60, world_text)
        self._draw_text_2d(10, 85, type_text)

        # Status text: center if won, otherwise bottom-left
        if self.game_state == "won":
            center_x = self.width // 2 - 220
            center_y = self.height // 2 - 20
            self._draw_text_2d(center_x, center_y, status_text)
        else:
            self._draw_text_2d(10, 115, status_text)

        # Hint text (under status)
        self._draw_text_2d(10, 140, hint_text)

        self._end_2d()

    def _apply_cell_effect(self, row, col, entered_new):
        """
        Apply per-cell effects:
        - continuous: slow / speed (while inside the cell)
        - one-shot (on enter): reset / turn / launch
        """
        # Guard against weird indices, though collisions should prevent it.
        if not (0 <= row < self.maze.rows and 0 <= col < self.maze.cols):
            self.player.move_speed = self.base_move_speed
            return

        cell = self.maze.grid[row][col]
        ctype = cell["type"]

        # Default speed
        self.player.move_speed = self.base_move_speed

        # Continuous modifiers
        if ctype == "slow":
            self.player.move_speed = self.base_move_speed * 0.5
        elif ctype == "speed":
            self.player.move_speed = self.base_move_speed * 1.8

        # One-shot effects only when we *enter* the cell
        if not entered_new:
            return

        if ctype == "reset":
            # Trap: send player back to start, but keep time running
            start_pos = self.maze.get_entrance_world_position()
            self.player.set_position(*start_pos)
            self.player.yaw = self.maze.get_entry_yaw()
            self.player.pitch = 0.0

            r0, c0 = self.maze.world_to_cell_indices(
                self.player.position[0],
                self.player.position[2],
            )
            self.current_cell = (r0, c0)

        elif ctype == "turn":
            # Rotate 90 degrees
            self.player.yaw += 90.0

        elif ctype == "launch":
            # Strong upward kick so the player can see over the walls
            self.player.vertical_velocity = self.player.jump_speed * 2.5

    def run(self):
        """
        Main game loops
        """
        while self.running:
            dt_ms = self.clock.tick(TARGET_FPS)
            dt = dt_ms / 1000.0

            mouse_dx, mouse_dy = self.handle_events()
            self.update(dt, mouse_dx, mouse_dy)
            self.draw_scene()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

# -----------------------------
# Entry point
# -----------------------------

if __name__ == "__main__":
    Game().run()

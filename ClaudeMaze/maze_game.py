"""
Interactive 3D Maze Game
COSC 4370 Computer Graphics HW5

Controls:
- WASD: Move through maze
- Mouse: Look around
- R: Reset to start (keep same maze)
- G: Generate new maze
- ESC: Exit
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import time
import os

# ============================================================================
# TEXTURE LOADING
# ============================================================================

def load_texture(filename):
    """Load a texture from file and return texture ID"""
    try:
        texture_surface = pygame.image.load(filename)
        texture_data = pygame.image.tostring(texture_surface, "RGB", True)
        width, height = texture_surface.get_size()
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        # Upload texture data
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        
        return texture_id
    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
        return None

# ============================================================================
# CONSTANTS
# ============================================================================

# Maze dimensions
MAZE_WIDTH = 10
MAZE_HEIGHT = 10
CELL_SIZE = 4.0  # Each cell is 4x4 units in world space
WALL_HEIGHT = 3.0
WALL_THICKNESS = 0.2  # Thickness of walls

# Texture settings
WALL_TEXTURE_SCALE_U = 0.5  # Horizontal texture repeat factor (higher = more repeats)
WALL_TEXTURE_SCALE_V = 0.5  # Vertical texture repeat factor (higher = more repeats)
FLOOR_TEXTURE_SCALE_U = 1.0
FLOOR_TEXTURE_SCALE_V = 1.0

# Player settings
PLAYER_HEIGHT = 0.5
PLAYER_SPEED = 5.0
MOUSE_SENSITIVITY = 0.0006

# Camera settings
CAMERA_DISTANCE = 7.0  # Distance behind/above player
CAMERA_HEIGHT = 8.0
CAMERA_ANGLE = 45.0  # Degrees looking down

# ============================================================================
# ROOM TYPES
# ============================================================================

class RoomType:
    """Different room types with different effects"""
    NORMAL = 0
    START = 1
    END = 2
    SLOW = 3
    TRAP = 4
    SPEED = 5
    SPINNER = 6
    LAUNCHER = 7
    CLUE = 8

    @staticmethod
    def get_name(room_type):
        """Return name for each room type"""
        names = {
            RoomType.NORMAL: "Normal",
            RoomType.START: "Start",
            RoomType.END: "End",
            RoomType.SLOW: "Slow",
            RoomType.TRAP: "Trap",
            RoomType.SPEED: "Speed Boost",
            RoomType.SPINNER: "Spinner",
            RoomType.LAUNCHER: "Launcher",
            RoomType.CLUE: "Clue"
        }
        return names.get(room_type, "Unknown")

    @staticmethod
    def get_texture_filename(room_type):
        """Return texture filename for each room type"""
        textures = {
            RoomType.NORMAL: "brick.jpg",
            RoomType.START: "brick2.jpg",
            RoomType.END: "wood.jpg",
            RoomType.SLOW: "grass.jpg",
            RoomType.TRAP: "lava.jpg",
            RoomType.SPEED: "metal_floor.jpg",
            RoomType.SPINNER: "dark_marble.jpg",
            RoomType.LAUNCHER: "metal_grate.jpg",
            RoomType.CLUE: "clue.jpg"
        }
        return textures.get(room_type, "normal.jpg")

    @staticmethod
    def get_descrip(room_type):
        descrips = {
            RoomType.NORMAL: "Standard Grid",
            RoomType.START: "Starting grid for maze",
            RoomType.END: "End grid for maze",
            RoomType.SLOW: "Slows movespeed while in grid",
            RoomType.TRAP: "Resets player to start of maze",
            RoomType.SPEED: "Increases movespeed while in grid",
            RoomType.SPINNER: "Randomly spins you to a new angle",
            RoomType.LAUNCHER: "Get a quick birds eye view",
            RoomType.CLUE: "The best possible path through the maze is highlighted for a short time",
        }
        return descrips.get(room_type, "Unknown")
# ============================================================================
# CELL CLASS
# ============================================================================

class Cell:
    """Represents a single cell in the maze"""
    def __init__(self, x, z):
        self.x = x  # Grid position
        self.z = z
        self.walls = {
            'N': True,  # North wall
            'S': True,  # South wall
            'E': True,  # East wall
            'W': True   # West wall
        }
        self.visited = False  # For maze generation
        self.room_type = RoomType.NORMAL
        self.effect_active = True  # Can room effect be triggered?

# ============================================================================
# MAZE CLASS
# ============================================================================

class Maze:
    """Generates and manages the maze structure"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [[Cell(x, z) for z in range(height)] for x in range(width)]
        self.start_pos = (0, 0)
        self.end_pos = (width - 1, height - 1)
        self.solution_path = []
        self.generate()
        self.assign_room_types()

    def generate(self):
        """Generate maze using recursive backtracker algorithm"""
        # Reset all cells
        for row in self.cells:
            for cell in row:
                cell.visited = False
                cell.walls = {'N': True, 'S': True, 'E': True, 'W': True}

        # Start from (0, 0)
        stack = [(0, 0)]
        self.cells[0][0].visited = True

        while stack:
            x, z = stack[-1]
            neighbors = self.get_unvisited_neighbors(x, z)

            if neighbors:
                # Choose random unvisited neighbor
                nx, nz, direction = random.choice(neighbors)

                # Remove walls between current and neighbor
                self.remove_wall_between(x, z, nx, nz, direction)

                # Mark neighbor as visited and add to stack
                self.cells[nx][nz].visited = True
                stack.append((nx, nz))
            else:
                stack.pop()

        # Find solution path for special room placement
        self.find_solution_path()

        # Remove entrance and exit walls
        self.remove_entrance_exit_walls()

    def get_unvisited_neighbors(self, x, z):
        """Get list of unvisited neighbors"""
        neighbors = []

        # North
        if z > 0 and not self.cells[x][z - 1].visited:
            neighbors.append((x, z - 1, 'N'))
        # South
        if z < self.height - 1 and not self.cells[x][z + 1].visited:
            neighbors.append((x, z + 1, 'S'))
        # East
        if x < self.width - 1 and not self.cells[x + 1][z].visited:
            neighbors.append((x + 1, z, 'E'))
        # West
        if x > 0 and not self.cells[x - 1][z].visited:
            neighbors.append((x - 1, z, 'W'))

        return neighbors

    def remove_wall_between(self, x1, z1, x2, z2, direction):
        """Remove walls between two cells to create passage"""
        opposite = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

        self.cells[x1][z1].walls[direction] = False
        self.cells[x2][z2].walls[opposite[direction]] = False

    def find_solution_path(self):
        """Find the solution path from start to end using BFS"""
        from collections import deque

        queue = deque([self.start_pos])
        visited = {self.start_pos: None}

        while queue:
            current = queue.popleft()

            if current == self.end_pos:
                # Reconstruct path
                path = []
                node = current
                while node is not None:
                    path.append(node)
                    node = visited[node]
                self.solution_path = path[::-1]
                return

            x, z = current
            cell = self.cells[x][z]

            # Check each direction
            if not cell.walls['N'] and z > 0:
                neighbor = (x, z - 1)
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)

            if not cell.walls['S'] and z < self.height - 1:
                neighbor = (x, z + 1)
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)

            if not cell.walls['E'] and x < self.width - 1:
                neighbor = (x + 1, z)
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)

            if not cell.walls['W'] and x > 0:
                neighbor = (x - 1, z)
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)

    def remove_entrance_exit_walls(self):
        """Remove outer walls at entrance (start) and exit (end) positions"""
        sx, sz = self.start_pos
        ex, ez = self.end_pos

        start_cell = self.cells[sx][sz]
        end_cell = self.cells[ex][ez]

        # Remove west wall at start (entrance on left side)
        start_cell.walls['W'] = False

        # Remove east wall at end (exit on right side)
        end_cell.walls['E'] = False

    def assign_room_types(self):
        """Assign special room types to cells"""
        # Mark start and end
        sx, sz = self.start_pos
        ex, ez = self.end_pos
        self.cells[sx][sz].room_type = RoomType.START
        self.cells[ex][ez].room_type = RoomType.END

        # Convert solution path to set for quick lookup
        solution_set = set(self.solution_path)

        # Assign special rooms
        for x in range(self.width):
            for z in range(self.height):
                if (x, z) in [(sx, sz), (ex, ez)]:
                    continue  # Skip start and end

                cell = self.cells[x][z]

                # Check if dead end
                wall_count = sum(1 for w in cell.walls.values() if w)
                is_dead_end = wall_count == 3

                # Dead ends get traps (reset to start)
                if is_dead_end:
                    cell.room_type = RoomType.TRAP

                # Solution path gets speed boosts
                elif (x, z) in solution_set and random.random() < 0.25:
                    cell.room_type = RoomType.SPEED

                # Off main path gets various effects
                elif (x, z) not in solution_set:
                    rand = random.random()
                    if rand < 0.15:
                        cell.room_type = RoomType.SLOW
                    elif rand < 0.18:
                        cell.room_type = RoomType.SPINNER
                    elif rand < 0.2:
                        cell.room_type = RoomType.LAUNCHER
                    elif rand < 0.23:
                        cell.room_type = RoomType.CLUE

    def get_cell(self, x, z):
        """Safely get a cell"""
        if 0 <= x < self.width and 0 <= z < self.height:
            return self.cells[x][z]
        return None

# ============================================================================
# PLAYER CLASS
# ============================================================================

class Player:
    """Represents the player in the maze"""
    def __init__(self, x, z):
        self.x = x
        self.y = PLAYER_HEIGHT
        self.z = z
        self.angle = 0  # Rotation angle (radians)
        self.base_speed = PLAYER_SPEED
        self.speed = PLAYER_SPEED
        self.velocity_y = 0  # For jumping/launching
        self.is_airborne = False
        self.active_effects = []

    def update(self, dt, keys, maze):
        """Update player position and handle movement"""
        # Calculate movement direction
        forward = 0
        strafe = 0

        if keys[K_w]:
            forward += 1
        if keys[K_s]:
            forward -= 1
        if keys[K_a]:
            strafe -= 1
        if keys[K_d]:
            strafe += 1

        # Convert to world space movement
        dx = (forward * math.cos(self.angle) + strafe * math.cos(self.angle + math.pi/2)) * self.speed * dt
        dz = (forward * math.sin(self.angle) + strafe * math.sin(self.angle + math.pi/2)) * self.speed * dt

        # Try to move
        new_x = self.x + dx
        new_z = self.z + dz

        if not self.check_collision(new_x, new_z, maze):
            self.x = new_x
            self.z = new_z

        # Handle vertical movement (jumping/launching)
        if self.is_airborne:
            self.velocity_y -= 9.8 * dt  # Gravity
            self.y += self.velocity_y * dt

            if self.y <= PLAYER_HEIGHT:
                self.y = PLAYER_HEIGHT
                self.is_airborne = False
                self.velocity_y = 0

        # Apply room effects
        self.apply_room_effects(maze)

    def check_collision(self, new_x, new_z, maze):
        """Check if movement would collide with walls"""
        # Which cell are we trying to enter?
        cell_x = int(new_x / CELL_SIZE)
        cell_z = int(new_z / CELL_SIZE)

        # Boundary check
        if not (0 <= cell_x < maze.width and 0 <= cell_z < maze.height):
            return True  # Collision with world bounds

        cell = maze.cells[cell_x][cell_z]

        # Check walls within the cell
        local_x = new_x % CELL_SIZE
        local_z = new_z % CELL_SIZE
        margin = 0.5  # Collision margin

        # Check each wall
        if cell.walls['N'] and local_z < margin:
            return True
        if cell.walls['S'] and local_z > CELL_SIZE - margin:
            return True
        if cell.walls['W'] and local_x < margin:
            return True
        if cell.walls['E'] and local_x > CELL_SIZE - margin:
            return True

        return False

    def apply_room_effects(self, maze):
        """Apply effects based on current room"""
        cell_x = int(self.x / CELL_SIZE)
        cell_z = int(self.z / CELL_SIZE)

        if not (0 <= cell_x < maze.width and 0 <= cell_z < maze.height):
            return

        cell = maze.cells[cell_x][cell_z]

        # Apply room effects (only once per entry)
        if cell.effect_active:
            if cell.room_type == RoomType.SLOW:
                self.speed = self.base_speed * 0.5
            elif cell.room_type == RoomType.SPEED:
                self.speed = self.base_speed * 1.5
            elif cell.room_type == RoomType.SPINNER:
                self.angle += math.pi / 2  # Turn 90 degrees
                cell.effect_active = False  # Only spin once
            elif cell.room_type == RoomType.TRAP:
                # Will be handled by game to reset position
                pass
            elif cell.room_type == RoomType.LAUNCHER:
                self.velocity_y = 15.0
                self.is_airborne = True
                cell.effect_active = False
            else:
                self.speed = self.base_speed
        else:
            # Reset speed for non-special rooms
            if cell.room_type in [RoomType.NORMAL, RoomType.START, RoomType.END]:
                self.speed = self.base_speed

    def get_current_cell(self, maze):
        """Get the cell the player is currently in"""
        cell_x = int(self.x / CELL_SIZE)
        cell_z = int(self.z / CELL_SIZE)
        return maze.get_cell(cell_x, cell_z)

    def reset_position(self, maze):
        """Reset player to start position"""
        sx, sz = maze.start_pos
        self.x = sx * CELL_SIZE + CELL_SIZE / 2
        self.z = sz * CELL_SIZE + CELL_SIZE / 2
        self.y = PLAYER_HEIGHT
        self.angle = 0
        self.speed = self.base_speed
        self.is_airborne = False
        self.velocity_y = 0

# ============================================================================
# RENDERING FUNCTIONS
# ============================================================================

def setup_lighting():
    """Set up OpenGL lighting"""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Light position (above the maze)
    glLightfv(GL_LIGHT0, GL_POSITION, [MAZE_WIDTH * CELL_SIZE / 2, 20, MAZE_HEIGHT * CELL_SIZE / 2, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.6, 0.6, 0.6, 1.0])  # Increased ambient light
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # Increased diffuse light
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])

    # Increase global ambient light
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.4, 0.4, 0.4, 1.0])


def render_floor(world_x, world_z, cell, brightness=1.0, floor_textures=None):
    """Render a floor tile with texture"""
    # Check if we have a texture for this room type
    use_texture = floor_textures is not None and cell.room_type in floor_textures and floor_textures[
        cell.room_type] is not None

    # Temporarily disable lighting for floors to show textures properly
    glDisable(GL_LIGHTING)

    if use_texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, floor_textures[cell.room_type])
        glColor3f(brightness, brightness, brightness)  # Use brightness as tint

        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)  # Normal pointing up for proper lighting
        glTexCoord2f(0, 0);
        glVertex3f(world_x, 0, world_z)
        glTexCoord2f(1, 0);
        glVertex3f(world_x + CELL_SIZE, 0, world_z)
        glTexCoord2f(1, 1);
        glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
        glTexCoord2f(0, 1);
        glVertex3f(world_x, 0, world_z + CELL_SIZE)
        glEnd()

        glDisable(GL_TEXTURE_2D)
    else:
        # If no texture, render a default gray floor
        glColor3f(0.5, 0.5, 0.5)

        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(world_x, 0, world_z)
        glVertex3f(world_x + CELL_SIZE, 0, world_z)
        glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
        glVertex3f(world_x, 0, world_z + CELL_SIZE)
        glEnd()

    # Re-enable lighting for other objects
    glEnable(GL_LIGHTING)

def render_wall(world_x, world_z, direction, brick_texture=None):
    """Render a wall with thickness and optional brick texture"""
    # Side color (dark gray) - used if no texture
    side_color = (0.2, 0.2, 0.2)
    # Top color (black for maximum contrast)
    top_color = (0.0, 0.0, 0.0)

    # Enable texturing if we have a brick texture
    use_texture = brick_texture is not None
    if use_texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, brick_texture)
        glColor3f(1.0, 1.0, 1.0)  # White color so texture shows true colors
    else:
        glColor3f(*side_color)

    if direction == 'N':  # North wall (along x-axis at z=world_z)
        # Front face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z)
        else:
            glVertex3f(world_x, 0, world_z)
            glVertex3f(world_x + CELL_SIZE, 0, world_z)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
            glVertex3f(world_x, WALL_HEIGHT, world_z)
        glEnd()

        # Back face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z + WALL_THICKNESS)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z + WALL_THICKNESS)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + WALL_THICKNESS)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z + WALL_THICKNESS)
        else:
            glVertex3f(world_x, 0, world_z + WALL_THICKNESS)
            glVertex3f(world_x, WALL_HEIGHT, world_z + WALL_THICKNESS)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + WALL_THICKNESS)
            glVertex3f(world_x + CELL_SIZE, 0, world_z + WALL_THICKNESS)
        glEnd()

        # Left end
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z + WALL_THICKNESS)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x, 0, world_z + WALL_THICKNESS)
        else:
            glVertex3f(world_x, 0, world_z)
            glVertex3f(world_x, WALL_HEIGHT, world_z)
            glVertex3f(world_x, WALL_HEIGHT, world_z + WALL_THICKNESS)
            glVertex3f(world_x, 0, world_z + WALL_THICKNESS)
        glEnd()

        # Right end
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z + WALL_THICKNESS)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + WALL_THICKNESS)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
        else:
            glVertex3f(world_x + CELL_SIZE, 0, world_z)
            glVertex3f(world_x + CELL_SIZE, 0, world_z + WALL_THICKNESS)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + WALL_THICKNESS)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
        glEnd()

        # Top (darker, no texture)
        if use_texture:
            glDisable(GL_TEXTURE_2D)
        glColor3f(*top_color)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(world_x, WALL_HEIGHT, world_z)
        glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
        glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + WALL_THICKNESS)
        glVertex3f(world_x, WALL_HEIGHT, world_z + WALL_THICKNESS)
        glEnd()
        if use_texture:
            glEnable(GL_TEXTURE_2D)
            glColor3f(1.0, 1.0, 1.0)

    elif direction == 'S':  # South wall
        # Front face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z + CELL_SIZE)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
        else:
            glVertex3f(world_x, 0, world_z + CELL_SIZE)
            glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
        glEnd()

        # Back face
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z + CELL_SIZE - WALL_THICKNESS)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE - WALL_THICKNESS)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
        else:
            glVertex3f(world_x, 0, world_z + CELL_SIZE - WALL_THICKNESS)
            glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE - WALL_THICKNESS)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
            glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
        glEnd()

        # Left end
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z + CELL_SIZE - WALL_THICKNESS)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x, 0, world_z + CELL_SIZE)
        else:
            glVertex3f(world_x, 0, world_z + CELL_SIZE - WALL_THICKNESS)
            glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
            glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x, 0, world_z + CELL_SIZE)
        glEnd()

        # Right end
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE - WALL_THICKNESS)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
        else:
            glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE - WALL_THICKNESS)
            glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
        glEnd()

        # Top (darker, no texture)
        if use_texture:
            glDisable(GL_TEXTURE_2D)
        glColor3f(*top_color)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
        glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE - WALL_THICKNESS)
        glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
        glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
        glEnd()
        if use_texture:
            glEnable(GL_TEXTURE_2D)
            glColor3f(1.0, 1.0, 1.0)

    elif direction == 'E':  # East wall
        # Front face
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
        else:
            glVertex3f(world_x + CELL_SIZE, 0, world_z)
            glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
        glEnd()

        # Back face
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, 0, world_z)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, 0, world_z + CELL_SIZE)
        else:
            glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, 0, world_z)
            glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z)
            glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, 0, world_z + CELL_SIZE)
        glEnd()

        # Near end
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, 0, world_z)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z)
        else:
            glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, 0, world_z)
            glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
            glVertex3f(world_x + CELL_SIZE, 0, world_z)
        glEnd()

        # Far end
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, 0, world_z + CELL_SIZE)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
        else:
            glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, 0, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE, 0, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
        glEnd()

        # Top (darker, no texture)
        if use_texture:
            glDisable(GL_TEXTURE_2D)
        glColor3f(*top_color)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z)
        glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z)
        glVertex3f(world_x + CELL_SIZE, WALL_HEIGHT, world_z + CELL_SIZE)
        glVertex3f(world_x + CELL_SIZE - WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
        glEnd()
        if use_texture:
            glEnable(GL_TEXTURE_2D)
            glColor3f(1.0, 1.0, 1.0)

    elif direction == 'W':  # West wall
        # Front face
        glBegin(GL_QUADS)
        glNormal3f(1, 0, 0)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x, 0, world_z + CELL_SIZE)
        else:
            glVertex3f(world_x, 0, world_z)
            glVertex3f(world_x, WALL_HEIGHT, world_z)
            glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x, 0, world_z + CELL_SIZE)
        glEnd()

        # Back face
        glBegin(GL_QUADS)
        glNormal3f(-1, 0, 0)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x + WALL_THICKNESS, 0, world_z)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + WALL_THICKNESS, 0, world_z + CELL_SIZE)
            glTexCoord2f(CELL_SIZE * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z)
        else:
            glVertex3f(world_x + WALL_THICKNESS, 0, world_z)
            glVertex3f(world_x + WALL_THICKNESS, 0, world_z + CELL_SIZE)
            glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z)
        glEnd()

        # Near end
        glBegin(GL_QUADS)
        glNormal3f(0, 0, -1)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + WALL_THICKNESS, 0, world_z)
        else:
            glVertex3f(world_x, 0, world_z)
            glVertex3f(world_x, WALL_HEIGHT, world_z)
            glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z)
            glVertex3f(world_x + WALL_THICKNESS, 0, world_z)
        glEnd()

        # Far end
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        if use_texture:
            glTexCoord2f(0, 0); glVertex3f(world_x, 0, world_z + CELL_SIZE)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, 0); glVertex3f(world_x + WALL_THICKNESS, 0, world_z + CELL_SIZE)
            glTexCoord2f(WALL_THICKNESS * WALL_TEXTURE_SCALE_U, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
            glTexCoord2f(0, WALL_HEIGHT * WALL_TEXTURE_SCALE_V); glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
        else:
            glVertex3f(world_x, 0, world_z + CELL_SIZE)
            glVertex3f(world_x + WALL_THICKNESS, 0, world_z + CELL_SIZE)
            glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
            glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
        glEnd()

        # Top (darker, no texture)
        if use_texture:
            glDisable(GL_TEXTURE_2D)
        glColor3f(*top_color)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glVertex3f(world_x, WALL_HEIGHT, world_z)
        glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z)
        glVertex3f(world_x + WALL_THICKNESS, WALL_HEIGHT, world_z + CELL_SIZE)
        glVertex3f(world_x, WALL_HEIGHT, world_z + CELL_SIZE)
        glEnd()
        if use_texture:
            glEnable(GL_TEXTURE_2D)
            glColor3f(1.0, 1.0, 1.0)

    # Cleanup - disable texture after rendering
    if use_texture:
        glDisable(GL_TEXTURE_2D)

def render_player(player):
    """Render player as a glowing ball"""
    glPushMatrix()
    glTranslatef(player.x, player.y, player.z)

    # Disable lighting for glowing effect
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.8)  # Warm white/yellow glow

    # Render sphere
    quadric = gluNewQuadric()
    gluSphere(quadric, 0.3, 16, 16)
    gluDeleteQuadric(quadric)

    glEnable(GL_LIGHTING)
    glPopMatrix()


def render_maze(maze, player, wall_texture=None, floor_textures=None, show_path=False):
    """Render the entire maze"""
    for x in range(maze.width):
        for z in range(maze.height):
            cell = maze.cells[x][z]
            world_x = x * CELL_SIZE
            world_z = z * CELL_SIZE

            # Render all cells at full brightness
            render_floor(world_x, world_z, cell, brightness=1.0, floor_textures=floor_textures)

            # Render walls with brick texture
            if cell.walls['N']:
                render_wall(world_x, world_z, 'N', wall_texture)
            if cell.walls['S']:
                render_wall(world_x, world_z, 'S', wall_texture)
            if cell.walls['E']:
                render_wall(world_x, world_z, 'E', wall_texture)
            if cell.walls['W']:
                render_wall(world_x, world_z, 'W', wall_texture)

    # Highlight the solution path if enabled
    if show_path:
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 0.0, 0.6)  # Yellow with transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Disable depth writing so the overlay doesn't interfere with walls
        glDepthMask(GL_FALSE)

        for (x, z) in maze.solution_path:
            world_x = x * CELL_SIZE
            world_z = z * CELL_SIZE

            # Draw a highlighted overlay on the floor
            glBegin(GL_QUADS)
            glVertex3f(world_x + 0.2, 0.1, world_z + 0.2)
            glVertex3f(world_x + CELL_SIZE - 0.2, 0.1, world_z + 0.2)
            glVertex3f(world_x + CELL_SIZE - 0.2, 0.1, world_z + CELL_SIZE - 0.2)
            glVertex3f(world_x + 0.2, 0.1, world_z + CELL_SIZE - 0.2)
            glEnd()

        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

def render_hud(screen, player, maze, elapsed_time):
    """Render HUD with time and position"""
    font = pygame.font.Font(None, 36)

    # Format time
    minutes = int(elapsed_time // 60)
    seconds = elapsed_time % 60
    time_text = f"Time: {minutes:02d}:{seconds:05.2f}"

    # Position
    cell_x = int(player.x / CELL_SIZE)
    cell_z = int(player.z / CELL_SIZE)
    pos_text = f"Position: ({cell_x}, {cell_z})"


    # Render text
    time_surface = font.render(time_text, True, (255, 255, 255))
    pos_surface = font.render(pos_text, True, (255, 255, 255))

    # Convert to OpenGL texture and draw
    # For now, just store for pygame overlay
    return time_surface, pos_surface

# ============================================================================
# GAME CLASS
# ============================================================================

class Game:
    """Main game class"""
    def __init__(self):
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Maze Game")

        # Hide and capture mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        # Set up OpenGL
        self.setup_opengl()

        # Load textures
        # Try to load brick texture from textures folder
        texture_path = os.path.join("textures", "rough_stone.jpg")
        self.brick_texture = load_texture(texture_path)
        if self.brick_texture:
            print(f"Loaded brick texture from {texture_path}")
        else:
            print(f"Warning: Could not load brick texture from {texture_path}")

        # Load floor textures for different room types
        self.floor_textures = {}
        loaded_textures = {}  # Cache to avoid loading same file multiple times

        for room_type in [RoomType.NORMAL, RoomType.START, RoomType.END,
                          RoomType.SLOW, RoomType.TRAP, RoomType.SPEED,
                          RoomType.SPINNER, RoomType.LAUNCHER, RoomType.CLUE]:

            texture_filename = RoomType.get_texture_filename(room_type)

            # Check if we've already loaded this texture file
            if texture_filename in loaded_textures:
                self.floor_textures[room_type] = loaded_textures[texture_filename]
            else:
                # Load new texture
                texture_path = os.path.join("textures", texture_filename)
                texture_id = load_texture(texture_path)

                if texture_id:
                    print(f"Loaded {texture_filename} for {RoomType.get_name(room_type)}")
                    self.floor_textures[room_type] = texture_id
                    loaded_textures[texture_filename] = texture_id
                else:
                    print(f"Warning: Could not load {texture_filename} for {RoomType.get_name(room_type)}")
                    self.floor_textures[room_type] = None

        # Create maze and player
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        start_x, start_z = self.maze.start_pos
        self.player = Player(start_x * CELL_SIZE + CELL_SIZE / 2, start_z * CELL_SIZE + CELL_SIZE / 2)

        # Game state
        self.running = True
        self.clock = pygame.time.Clock()
        self.start_time = time.time()
        self.elapsed_time = 0

        # Path highlighting state
        self.show_path = False
        self.path_end_time = 0

        # Font for HUD
        self.font = pygame.font.Font(None, 36)

    def setup_opengl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        # Disable backface culling so walls are visible from both sides
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)

        # Set up projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.screen_width / self.screen_height, 0.1, 100.0)

        # Set up lighting
        setup_lighting()

        glMatrixMode(GL_MODELVIEW)

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_r:
                    # Reset to start
                    self.player.reset_position(self.maze)
                    self.start_time = time.time()
                    # Re-enable room effects
                    for row in self.maze.cells:
                        for cell in row:
                            cell.effect_active = True

                elif event.key == K_g:
                    # Generate new maze
                    self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
                    self.player.reset_position(self.maze)
                    self.start_time = time.time()

            elif event.type == MOUSEMOTION:
                # Handle mouse look
                dx = event.rel[0]
                self.player.angle -= dx * MOUSE_SENSITIVITY

    def update(self, dt):
        """Update game state"""
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.maze)

        # Check for trap trigger
        current_cell = self.player.get_current_cell(self.maze)
        if current_cell and current_cell.room_type == RoomType.TRAP and current_cell.effect_active:
            self.player.reset_position(self.maze)
            self.start_time = time.time()
            # Re-enable all room effects after trap reset
            for row in self.maze.cells:
                for cell in row:
                    cell.effect_active = True

        # Check for clue trigger
        if current_cell and current_cell.room_type == RoomType.CLUE and current_cell.effect_active:
            self.show_path = True
            self.path_end_time = time.time() + 7.0  # Show path for 10 seconds
            current_cell.effect_active = False  # Only trigger once

        # Check if path highlighting should end
        if self.show_path and time.time() >= self.path_end_time:
            self.show_path = False

        # Update elapsed time
        self.elapsed_time = time.time() - self.start_time

        # Check for win condition
        end_x, end_z = self.maze.end_pos
        player_cell_x = int(self.player.x / CELL_SIZE)
        player_cell_z = int(self.player.z / CELL_SIZE)

        if player_cell_x == end_x and player_cell_z == end_z:
            print(f"You won! Time: {self.elapsed_time:.2f} seconds")

    def render(self):
        """Render the game"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Set up camera (top-down angled view)
        cam_x = self.player.x - CAMERA_DISTANCE * math.cos(self.player.angle)
        cam_y = self.player.y + CAMERA_HEIGHT
        cam_z = self.player.z - CAMERA_DISTANCE * math.sin(self.player.angle)

        gluLookAt(
            cam_x, cam_y, cam_z,  # Camera position
            self.player.x, self.player.y, self.player.z,  # Look at player
            0, 1, 0  # Up vector
        )

        # Render maze and player
        render_maze(self.maze, self.player, self.brick_texture, self.floor_textures, self.show_path)
        render_player(self.player)

        # Render HUD using 2D overlay
        self.render_hud_overlay()

        pygame.display.flip()

    def render_hud_overlay(self):
        """Render HUD as 2D overlay"""
        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.screen_width, self.screen_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # Render time
        minutes = int(self.elapsed_time // 60)
        seconds = self.elapsed_time % 60
        time_text = f"Time: {minutes:02d}:{seconds:05.2f}"

        # Position
        cell_x = int(self.player.x / CELL_SIZE)
        cell_z = int(self.player.z / CELL_SIZE)
        pos_text = f"Position: ({cell_x}, {cell_z})"

        # Room type
        current_cell = self.player.get_current_cell(self.maze)
        if current_cell:
            room_name = RoomType.get_name(current_cell.room_type)
            room_text = f"Room: {room_name}"
        else:
            room_text = "Room: Unknown"

        # Description
        if current_cell:
            room_descrip = RoomType.get_descrip(current_cell.room_type)
            # Add (used) for spinners/launchers/clues that have been used
            if current_cell.room_type in [RoomType.SPINNER, RoomType.LAUNCHER, RoomType.CLUE] and not current_cell.effect_active:
                room_descrip += " (used)"
            room_effect = f"Description: {room_descrip}"
        else:
            room_effect = "Description: Unknown"

        # Controls
        controls_text = [
            "Controls:",
            "- WASD: Move through maze",
            "- Mouse: Look around",
            "- R: Reset player to start",
            "- G: Generate new maze",
            "- ESC: Exit"
        ]

        # Create text surfaces
        time_surface = self.font.render(time_text, True, (255, 255, 255))
        pos_surface = self.font.render(pos_text, True, (255, 255, 255))
        room_surface = self.font.render(room_text, True, (255, 255, 255))
        room_descrip = self.font.render(room_effect, True, (255, 255, 255))

        # Convert to OpenGL textures and render
        self.render_text_texture(time_surface, 10, 10)
        self.render_text_texture(pos_surface, 10, 50)
        self.render_text_texture(room_surface, 10, 90)
        self.render_text_texture(room_descrip, 10, 130)

        control_surfaces = [self.font.render(line, True, (255, 255, 255)) for line in controls_text]

        y_offset = 180
        for control_surface in control_surfaces:
            self.render_text_texture(control_surface, 10, y_offset)
            y_offset += 40

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        # Restore 3D projection
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def render_text_texture(self, surface, x, y):
        """Render a pygame surface as an OpenGL texture"""
        text_data = pygame.image.tostring(surface, "RGBA", True)
        width, height = surface.get_size()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 0); glVertex2f(x, y + height)
        glEnd()

        glDeleteTextures([texture])
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()
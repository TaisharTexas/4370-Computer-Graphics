# -*- coding: utf-8 -*-
"""
3D Maze Game
UIN:2062349
Author: Crystal
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import time
import math

# load textures from image files
def load_texture(filename):
    try:
        surface = pygame.image.load(filename)
        data = pygame.image.tostring(surface, "RGB", 1)
        width = surface.get_width()
        height = surface.get_height()
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
        
        return texture_id
    except Exception as e:
        print(f"Error loading texture: {e}")
        return None

def create_floor_texture():
    # make a checkered pattern if no image available
    width, height = 256, 256
    data = []
    
    for y in range(height):
        for x in range(width):
            if ((x // 32) + (y // 32)) % 2 == 0:
                data.extend([180, 200, 180])
            else:
                data.extend([150, 170, 150])
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes(data))
    
    return texture_id

def create_wall_texture():
    # brick pattern
    width, height = 256, 256
    data = []
    brick_height = 32
    brick_width = 64
    mortar_size = 4
    
    for y in range(height):
        for x in range(width):
            offset = (brick_width // 2) if (y // brick_height) % 2 == 1 else 0
            x_pos = (x + offset) % brick_width
            y_pos = y % brick_height
            
            if x_pos < mortar_size or y_pos < mortar_size:
                data.extend([100, 100, 110])
            else:
                variation = ((x // 8) + (y // 8)) % 20
                data.extend([80 + variation, 70 + variation, 85 + variation])
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes(data))
    
    return texture_id

class Maze:
    def __init__(self, size=10):
        self.size = size
        self.grid = [[1 for _ in range(size)] for _ in range(size)]
        self.generate()
        
    def generate(self):
        # using depth-first search to carve out paths
        stack = []
        start_x, start_y = 0, 0
        self.grid[start_y][start_x] = 0
        stack.append((start_x, start_y))
        
        while stack:
            current_x, current_y = stack[-1]
            neighbors = []
            directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
            
            for dx, dy in directions:
                nx, ny = current_x + dx, current_y + dy
                if (0 <= nx < self.size and 0 <= ny < self.size and 
                    self.grid[ny][nx] == 1):
                    neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                self.grid[current_y + dy//2][current_x + dx//2] = 0
                self.grid[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        
        self.grid[0][0] = 0
        self.grid[self.size-1][self.size-1] = 0
        if self.size > 1:
            self.grid[self.size-1][self.size-2] = 0
            self.grid[self.size-2][self.size-1] = 0
    
    def is_dead_end(self, x, y):
        # don't count start or goal as dead ends
        if (x == self.size - 1 and y == self.size - 1) or (x == 0 and y == 0):
            return False
        
        # see how many ways out there are
        exits = 0
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < self.size and 0 <= ny < self.size and 
                self.grid[ny][nx] == 0):
                exits += 1
        
        return exits == 1

class Player:
    def __init__(self):
        self.x = 0.5
        self.y = 0.5
        self.base_speed = 0.05
        self.speed_multiplier = 1.0
        
    def move(self, dx, dy, maze):
        speed = self.base_speed * self.speed_multiplier
        new_x = self.x + dx * speed
        new_y = self.y + dy * speed
        
        radius = 0.2
        can_move_x = self.can_move_to(new_x, self.y, maze, radius)
        can_move_y = self.can_move_to(self.x, new_y, maze, radius)
        
        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y
        
        return can_move_x or can_move_y
    
    def is_heading_to_dead_end(self, dx, dy, maze, distance=6.0):
        length = (dx**2 + dy**2)**0.5
        if length < 0.001:
            return False
        dx /= length
        dy /= length
        
        for i in range(1, 21):
            t = (i / 20) * distance
            test_x = self.x + dx * t
            test_y = self.y + dy * t
            
            grid_x = int(test_x)
            grid_y = int(test_y)
            
            if grid_x < 0 or grid_x >= maze.size or grid_y < 0 or grid_y >= maze.size:
                continue
            
            if maze.grid[grid_y][grid_x] == 1:
                break
            
            if maze.is_dead_end(grid_x, grid_y):
                return True
        
        return False
    
    def can_move_to(self, x, y, maze, radius):
        # check a bunch of points around the player so we don't clip through walls
        points = [
            (x, y),
            (x + radius, y), (x - radius, y),
            (x, y + radius), (x, y - radius),
            (x + radius * 0.707, y + radius * 0.707),
            (x - radius * 0.707, y + radius * 0.707),
            (x + radius * 0.707, y - radius * 0.707),
            (x - radius * 0.707, y - radius * 0.707),
        ]
        
        margin = 0.1
        for px, py in points:
            if px < margin or px > maze.size - margin or py < margin or py > maze.size - margin:
                return False
            
            grid_x = int(px)
            grid_y = int(py)
            
            if grid_x < 0 or grid_x >= maze.size or grid_y < 0 or grid_y >= maze.size:
                return False
            
            if maze.grid[grid_y][grid_x] == 1:
                return False
        
        return True

class PowerUp:
    def __init__(self, maze):
        self.x = None
        self.y = None
        self.active = True
        self.used = False
        self.spawn(maze)
        
    def spawn(self, maze):
        # put the powerup somewhere valid (not at start/goal or in dead ends)
        cells = []
        for row in range(maze.size):
            for col in range(maze.size):
                if (maze.grid[row][col] == 0 and 
                    not (col == 0 and row == 0) and 
                    not (col == maze.size - 1 and row == maze.size - 1) and
                    not maze.is_dead_end(col, row)):
                    cells.append((col, row))
        
        if not cells:
            for row in range(maze.size):
                for col in range(maze.size):
                    if (maze.grid[row][col] == 0 and 
                        not (col == 0 and row == 0) and 
                        not (col == maze.size - 1 and row == maze.size - 1)):
                        cells.append((col, row))
        
        if cells:
            self.x, self.y = random.choice(cells)
            self.active = True
            self.used = False
    
    def check_pickup(self, player):
        if self.active and not self.used:
            distance = ((player.x - (self.x + 0.5))**2 + (player.y - (self.y + 0.5))**2)**0.5
            if distance < 0.4:
                self.active = False
                self.used = True
                return True
        return False

def draw_cube(x, y, z, size, color, height=1.0, texture=None):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    half = size / 2
    h = height / 2
    
    vertices = [
        [-half, -h, -half], [half, -h, -half],
        [half, h, -half], [-half, h, -half],
        [-half, -h, half], [half, -h, half],
        [half, h, half], [-half, h, half]
    ]
    
    faces = [
        [0,1,2,3], [4,5,6,7], [0,1,5,4],
        [2,3,7,6], [0,3,7,4], [1,2,6,5]
    ]
    
    tex_coords = [[(0,0), (1,0), (1,1), (0,1)]] * 6
    
    if texture:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glColor3fv(color)
    
    glBegin(GL_QUADS)
    for face_idx, face in enumerate(faces):
        for vertex_idx, vertex in enumerate(face):
            if texture:
                glTexCoord2fv(tex_coords[face_idx][vertex_idx])
            glVertex3fv(vertices[vertex])
    glEnd()
    
    if texture:
        glDisable(GL_TEXTURE_2D)
    
    glPopMatrix()

def draw_maze(maze, player, floor_tex, wall_tex, powerup):
    cell_size = 1.0
    wall_height = 2.0
    size = maze.size * cell_size
    
    if floor_tex:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, floor_tex)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glColor3f(0.4, 0.5, 0.4)
    
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-size/2, 0, -size/2)
    glTexCoord2f(10, 0)
    glVertex3f(size/2, 0, -size/2)
    glTexCoord2f(10, 10)
    glVertex3f(size/2, 0, size/2)
    glTexCoord2f(0, 10)
    glVertex3f(-size/2, 0, size/2)
    glEnd()
    
    if floor_tex:
        glDisable(GL_TEXTURE_2D)
    
    half_size = (maze.size * cell_size) / 2
    
    for i in range(maze.size + 2):
        x = (i - 1) * cell_size - half_size + cell_size / 2
        z = -half_size - cell_size / 2
        draw_cube(x, wall_height/2, z, cell_size, (0.3, 0.3, 0.35), wall_height, wall_tex)
    
    for i in range(maze.size + 2):
        x = (i - 1) * cell_size - half_size + cell_size / 2
        z = half_size + cell_size / 2
        draw_cube(x, wall_height/2, z, cell_size, (0.3, 0.3, 0.35), wall_height, wall_tex)
    
    for i in range(maze.size):
        x = -half_size - cell_size / 2
        z = i * cell_size - half_size + cell_size / 2
        draw_cube(x, wall_height/2, z, cell_size, (0.3, 0.3, 0.35), wall_height, wall_tex)
    
    for i in range(maze.size):
        x = half_size + cell_size / 2
        z = i * cell_size - half_size + cell_size / 2
        draw_cube(x, wall_height/2, z, cell_size, (0.3, 0.3, 0.35), wall_height, wall_tex)
    
    for row in range(maze.size):
        for col in range(maze.size):
            x = col * cell_size - (maze.size * cell_size) / 2 + cell_size / 2
            z = row * cell_size - (maze.size * cell_size) / 2 + cell_size / 2
            
            if maze.grid[row][col] == 1:
                draw_cube(x, wall_height/2, z, cell_size, (0.15, 0.15, 0.2), wall_height, wall_tex)
    
    if powerup and powerup.active and not powerup.used:
        item_x = powerup.x * cell_size - (maze.size * cell_size) / 2 + cell_size / 2
        item_z = powerup.y * cell_size - (maze.size * cell_size) / 2 + cell_size / 2
        offset = time.time() * 2
        item_y = 0.3 + 0.1 * math.sin(time.time() * 3)
        
        glPushMatrix()
        glTranslatef(item_x, item_y, item_z)
        glRotatef(offset * 50, 0, 1, 0)
        
        glColor3f(0.2, 0.8, 1.0)
        sz = 0.25
        
        glBegin(GL_TRIANGLES)
        glVertex3f(0, sz, 0)
        glVertex3f(sz, 0, 0)
        glVertex3f(0, 0, sz)
        
        glVertex3f(0, sz, 0)
        glVertex3f(0, 0, sz)
        glVertex3f(-sz, 0, 0)
        
        glVertex3f(0, sz, 0)
        glVertex3f(-sz, 0, 0)
        glVertex3f(0, 0, -sz)
        
        glVertex3f(0, sz, 0)
        glVertex3f(0, 0, -sz)
        glVertex3f(sz, 0, 0)
        
        glVertex3f(0, -sz, 0)
        glVertex3f(0, 0, sz)
        glVertex3f(sz, 0, 0)
        
        glVertex3f(0, -sz, 0)
        glVertex3f(-sz, 0, 0)
        glVertex3f(0, 0, sz)
        
        glVertex3f(0, -sz, 0)
        glVertex3f(0, 0, -sz)
        glVertex3f(-sz, 0, 0)
        
        glVertex3f(0, -sz, 0)
        glVertex3f(sz, 0, 0)
        glVertex3f(0, 0, -sz)
        glEnd()
        
        glPopMatrix()
    
    goal_x = (maze.size - 1) * cell_size - (maze.size * cell_size) / 2 + cell_size / 2
    goal_z = (maze.size - 1) * cell_size - (maze.size * cell_size) / 2 + cell_size / 2
    draw_cube(goal_x, 0.5, goal_z, cell_size * 0.6, (1.0, 0.9, 0.0), 0.8)

def render_text(display, text, x, y):
    font = pygame.font.Font(None, 48)
    surface = font.render(text, True, (255, 255, 255))
    data = pygame.image.tostring(surface, "RGBA", True)
    width = surface.get_width()
    height = surface.get_height()
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, display[0], 0, display[1], -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x, y)
    glTexCoord2f(1, 0)
    glVertex2f(x + width, y)
    glTexCoord2f(1, 1)
    glVertex2f(x + width, y + height)
    glTexCoord2f(0, 1)
    glVertex2f(x, y + height)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glDeleteTextures([tex])

def main():
    pygame.init()
    display = (800, 800)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("10x10 Maze - 3D View")
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    yaw = 45.0
    pitch = 20.0
    distance = 3.0
    sensitivity = 0.2
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    
    maze = Maze(10)
    player = Player()
    powerup = PowerUp(maze)
    
    is_launching = False
    launch_start = 0
    launch_duration = 3.0
    launch_height = 15.0
    warning = 0.0
    
    floor_tex = load_texture("RiceFloor.png")
    if not floor_tex:
        print("No floor texture found, using procedural texture")
        floor_tex = create_floor_texture()
    else:
        print("Floor texture loaded")
    
    wall_tex = load_texture("WallGude.jpg")
    if not wall_tex:
        print("No wall texture found, using procedural brick texture")
        wall_tex = create_wall_texture()
    else:
        print("Wall texture loaded")
    
    start_time = time.time()
    clock = pygame.time.Clock()
    running = True
    
    keys = {'w': False, 's': False, 'a': False, 'd': False}
    
    print("Controls:")
    print("- W/A/S/D: Move")
    print("- Mouse: Look around")
    print("- R: New maze")
    print("- SPACE: Reset")
    print("- ESC: Exit")
    
    # main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                mouse_dx, mouse_dy = event.rel
                yaw -= mouse_dx * sensitivity
                pitch -= mouse_dy * sensitivity
                pitch = max(-89, min(89, pitch))
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    maze = Maze(10)
                    player = Player()
                    powerup = PowerUp(maze)
                    is_launching = False
                    warning = 0.0
                    start_time = time.time()
                    print("New maze generated")
                elif event.key == pygame.K_SPACE:
                    player = Player()
                    is_launching = False
                    warning = 0.0
                    start_time = time.time()
                    print("Reset to start")
                elif event.key == pygame.K_w:
                    keys['w'] = True
                elif event.key == pygame.K_s:
                    keys['s'] = True
                elif event.key == pygame.K_a:
                    keys['a'] = True
                elif event.key == pygame.K_d:
                    keys['d'] = True
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    keys['w'] = False
                elif event.key == pygame.K_s:
                    keys['s'] = False
                elif event.key == pygame.K_a:
                    keys['a'] = False
                elif event.key == pygame.K_d:
                    keys['d'] = False
        
        is_moving = any(keys.values())
        move_dx = 0
        move_dy = 0
        
        # figure out which way we're trying to move
        if keys['w']:
            move_dx += math.sin(math.radians(yaw))
            move_dy += math.cos(math.radians(yaw))
        
        if keys['s']:
            move_dx += -math.sin(math.radians(yaw))
            move_dy += -math.cos(math.radians(yaw))
        
        if keys['a']:
            move_dx += math.sin(math.radians(yaw + 90))
            move_dy += math.cos(math.radians(yaw + 90))
        
        if keys['d']:
            move_dx += math.sin(math.radians(yaw - 90))
            move_dy += math.cos(math.radians(yaw - 90))
        
        # check if player is heading into a dead end
        heading_to_dead_end = False
        if is_moving:
            heading_to_dead_end = player.is_heading_to_dead_end(move_dx, move_dy, maze)
        
        if heading_to_dead_end:
            warning = min(1.0, warning + 0.08)
            player.speed_multiplier = 0.5
        else:
            warning = max(0.0, warning - 0.05)
            player.speed_multiplier = 1.0
        
        if keys['w']:
            dx = math.sin(math.radians(yaw))
            dy = math.cos(math.radians(yaw))
            player.move(dx, dy, maze)
        
        if keys['s']:
            dx = -math.sin(math.radians(yaw))
            dy = -math.cos(math.radians(yaw))
            player.move(dx, dy, maze)
        
        if keys['a']:
            dx = math.sin(math.radians(yaw + 90))
            dy = math.cos(math.radians(yaw + 90))
            player.move(dx, dy, maze)
        
        if keys['d']:
            dx = math.sin(math.radians(yaw - 90))
            dy = math.cos(math.radians(yaw - 90))
            player.move(dx, dy, maze)
        
        goal_x = maze.size - 1 + 0.5
        goal_y = maze.size - 1 + 0.5
        dist_to_goal = ((player.x - goal_x)**2 + (player.y - goal_y)**2)**0.5
        
        if dist_to_goal < 0.5:
            elapsed = time.time() - start_time
            print(f"Goal reached in {elapsed:.2f} seconds!")
            maze = Maze(10)
            player = Player()
            powerup = PowerUp(maze)
            is_launching = False
            warning = 0.0
            start_time = time.time()
        
        if powerup.check_pickup(player):
            is_launching = True
            launch_start = time.time()
            print("Launch activated!")
        
        if is_launching:
            elapsed = time.time() - launch_start
            if elapsed >= launch_duration:
                is_launching = False
                print("Back to ground")
        
        grid_x = int(player.x)
        grid_y = int(player.y)
        if maze.is_dead_end(grid_x, grid_y):
            print("Dead end! Resetting...")
            player = Player()
            is_launching = False
            warning = 0.0
            start_time = time.time()
        
        elapsed = time.time() - start_time
        
        # set up camera position
        cell_size = 1.0
        px = player.x * cell_size - (maze.size * cell_size) / 2
        pz = player.y * cell_size - (maze.size * cell_size) / 2
        
        if is_launching:
            elapsed_launch = time.time() - launch_start
            # smooth up and down motion using easing
            if elapsed_launch < launch_duration / 2:
                t = elapsed_launch / (launch_duration / 2)
                t = t * t * (3 - 2 * t)
                cam_y = 0.5 + t * launch_height
            else:
                t = (elapsed_launch - launch_duration / 2) / (launch_duration / 2)
                t = t * t * (3 - 2 * t)
                cam_y = 0.5 + (1 - t) * launch_height
            
            pitch = -70
        else:
            cam_y = 0.5
        
        cam_x = px
        cam_z = pz
        
        look_dist = 10.0
        look_x = cam_x + look_dist * math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
        look_y = cam_y + look_dist * math.sin(math.radians(pitch))
        look_z = cam_z + look_dist * math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
        
        if not is_launching:
            pitch = max(-89, min(89, pitch))
        
        # draw everything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)
        
        draw_maze(maze, player, floor_tex, wall_tex, powerup)
        
        glDisable(GL_DEPTH_TEST)
        
        timer_text = f"Time: {int(elapsed // 60)}:{int(elapsed % 60):02d}"
        render_text(display, timer_text, 10, display[1] - 58)
        
        pos_text = f"Position: ({int(player.x)}, {int(player.y)})"
        font = pygame.font.Font(None, 48)
        surface = font.render(pos_text, True, (255, 255, 255))
        pos_x = display[0] - surface.get_width() - 10
        render_text(display, pos_text, pos_x, display[1] - 58)
        
        # draw red warning effect around edges if going wrong way
        if warning > 0.01:
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, display[0], 0, display[1], -1, 1)
            
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            vignette = 200
            alpha = warning * 0.6
            
            glBegin(GL_QUADS)
            
            glColor4f(0.8, 0.0, 0.0, alpha)
            glVertex2f(0, display[1])
            glVertex2f(display[0], display[1])
            glColor4f(0.8, 0.0, 0.0, 0)
            glVertex2f(display[0], display[1] - vignette)
            glVertex2f(0, display[1] - vignette)
            
            glColor4f(0.8, 0.0, 0.0, 0)
            glVertex2f(0, vignette)
            glVertex2f(display[0], vignette)
            glColor4f(0.8, 0.0, 0.0, alpha)
            glVertex2f(display[0], 0)
            glVertex2f(0, 0)
            
            glColor4f(0.8, 0.0, 0.0, alpha)
            glVertex2f(0, 0)
            glColor4f(0.8, 0.0, 0.0, 0)
            glVertex2f(vignette, 0)
            glVertex2f(vignette, display[1])
            glColor4f(0.8, 0.0, 0.0, alpha)
            glVertex2f(0, display[1])
            
            glColor4f(0.8, 0.0, 0.0, 0)
            glVertex2f(display[0] - vignette, 0)
            glColor4f(0.8, 0.0, 0.0, alpha)
            glVertex2f(display[0], 0)
            glVertex2f(display[0], display[1])
            glColor4f(0.8, 0.0, 0.0, 0)
            glVertex2f(display[0] - vignette, display[1])
            
            glEnd()
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            
            glDisable(GL_BLEND)
        
        glEnable(GL_DEPTH_TEST)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
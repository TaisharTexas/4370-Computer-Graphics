"""
3D Maze Game with Powerups and Traps
CSCI 4370 - Homework 5

Controls:
- W/A/S/D: Move forward/left/backward/right
- Mouse: Look around
- R: Reset position and time (same maze)
- N: New random maze
- ESC: Exit game
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import time

# MAZE GENERATION

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.maze = [[1 for _ in range(width)] for _ in range(height)]
        self.solution_path = []
        self.start_pos = (1, 1)  # interior start cell
        self.end_pos = (width - 2, height - 2)  # interior end cell
        self.start_entrance = (0, 1)  # outer wall entrance
        self.end_exit = (width - 1, height - 2)  # outer wall exit
        
    def generate(self):
        """generate maze using recursive backtracking"""
        self.maze = [[1 for _ in range(self.width)] for _ in range(self.height)]
        self.solution_path = []
        
        # start from (1, 1)
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = 0
        
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            
            # check all 4 directions (2 cells away)
            for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                    if self.maze[ny][nx] == 1:
                        neighbors.append((nx, ny, x + dx // 2, y + dy // 2))
            
            if neighbors:
                nx, ny, wx, wy = random.choice(neighbors)
                self.maze[wy][wx] = 0
                self.maze[ny][nx] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # pick random start and end positions on outer walls
        self._pick_random_entrances()
        
        # find solution path using BFS
        self._find_solution_path()
        
        return self.maze
    
    def _pick_random_entrances(self):
        """pick random start and end positions on the outer walls"""
        # get all valid edge cells (cells adjacent to outer wall that are paths)
        edge_cells = []
        
        # left wall (x=0): check cells at x=1
        for y in range(1, self.height - 1):
            if self.maze[y][1] == 0:
                edge_cells.append(((0, y), (1, y), 'left'))
        
        # right wall (x=width-1): check cells at x=width-2
        for y in range(1, self.height - 1):
            if self.maze[y][self.width - 2] == 0:
                edge_cells.append(((self.width - 1, y), (self.width - 2, y), 'right'))
        
        # top wall (y=0): check cells at y=1
        for x in range(1, self.width - 1):
            if self.maze[1][x] == 0:
                edge_cells.append(((x, 0), (x, 1), 'top'))
        
        # bottom wall (y=height-1): check cells at y=height-2
        for x in range(1, self.width - 1):
            if self.maze[self.height - 2][x] == 0:
                edge_cells.append(((x, self.height - 1), (x, self.height - 2), 'bottom'))
        
        # pick two random different edge cells for start and end
        # ensure minimum distance between start and end (at least half the maze size)
        min_distance = self.width // 2
        
        if len(edge_cells) >= 2:
            # try to find a pair with sufficient distance
            random.shuffle(edge_cells)
            best_start = None
            best_end = None
            best_distance = 0
            
            for start_choice in edge_cells:
                for end_choice in edge_cells:
                    if start_choice == end_choice:
                        continue
                    # calculate manhattan distance between interior positions
                    sx, sy = start_choice[1]
                    ex, ey = end_choice[1]
                    distance = abs(ex - sx) + abs(ey - sy)
                    
                    if distance >= min_distance:
                        # found a valid pair, use it
                        best_start = start_choice
                        best_end = end_choice
                        best_distance = distance
                        break
                    elif distance > best_distance:
                        # keep track of best pair in case none meet minimum
                        best_start = start_choice
                        best_end = end_choice
                        best_distance = distance
                
                if best_distance >= min_distance:
                    break
            
            # use best pair found (either meets minimum or is the furthest apart)
            if best_start and best_end:
                self.start_entrance = best_start[0]  # outer wall position
                self.start_pos = best_start[1]  # interior cell
                self.end_exit = best_end[0]  # outer wall position
                self.end_pos = best_end[1]  # interior cell
            else:
                # fallback to first two if somehow no pairs found
                self.start_entrance = edge_cells[0][0]
                self.start_pos = edge_cells[0][1]
                self.end_exit = edge_cells[1][0]
                self.end_pos = edge_cells[1][1]
            
            # open the entrance and exit in the maze
            self.maze[self.start_entrance[1]][self.start_entrance[0]] = 0
            self.maze[self.end_exit[1]][self.end_exit[0]] = 0
    
    def _find_solution_path(self):
        """find the solution path from start to end using BFS"""
        start = self.start_pos
        end = self.end_pos
        
        queue = [start]
        visited = {start: None}
        
        while queue:
            current = queue.pop(0)
            if current == end:
                break
                
            x, y = current
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.maze[ny][nx] == 0 and (nx, ny) not in visited:
                        visited[(nx, ny)] = current
                        queue.append((nx, ny))
        
        # reconstruct path
        self.solution_path = []
        current = end
        while current is not None:
            self.solution_path.append(current)
            current = visited.get(current)
        self.solution_path.reverse()
    
    def get_dead_ends(self):
        """Find all dead ends in the maze (cells with exactly 3 walls)"""
        dead_ends = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.maze[y][x] == 0:
                    walls = 0
                    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                        if self.maze[y + dy][x + dx] == 1:
                            walls += 1
                    # a dead end has exactly 3 walls 
                    # exclude start and end positions
                    if walls == 3 and (x, y) != self.start_pos and (x, y) != self.end_pos:
                        dead_ends.append((x, y))
        return dead_ends


# POWERUPS AND TRAPS

class PowerUp:
    SPEED_BOOST = 0
    JUMP_BOOST = 1
    
    def __init__(self, x, z, power_type):
        self.x = x
        self.z = z
        self.type = power_type
        self.collected = False
        self.rotation = 0
        self.bob_offset = random.random() * math.pi * 2


class Trap:
    SLOW = 0
    TELEPORT_START = 1
    SPIN = 2
    
    def __init__(self, x, z, trap_type, wall_facing=None):
        self.x = x
        self.z = z
        self.type = trap_type
        self.triggered = False
        self.cooldown = 0
        self.wall_facing = wall_facing  # direction the wall faces (for teleport trap image)


# PLAYER

class Player:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.x = 1.5
        self.y = 0.5
        self.z = 1.5
        self.yaw = 0
        self.pitch = 0
        self.speed = 3.8
        self.base_speed = 3.8
        self.speed_boost_time = 0
        self.slow_debuff_time = 0
        self.jumping = False
        self.jump_height = 0
        self.jump_time = 0
        self.jump_boost_active = False
        self.on_jump_pad = False  # track if player is on a jump pad
        self.can_move = True
        self.spin_time = 0
        self.spin_amount = 0
        self.is_jumping = False
        self.jump_velocity = 0
        self.ground_y = 0.5  # normal eye height
        self.jump_strength = 2.0  # moderate upward velocity for a visible hop
        self.gravity = 10.0  # gravity pulling player down
        self.leap_time = 0  # duration of the leap
        self.leap_duration = 0.25  # how long the leap lasts
        self.leap_speed = 8.0  # forward speed during leap
        self.leap_dir_x = 0  # direction of leap
        self.leap_dir_z = 0
        self.dead_end_message_time = 0  # timer for dead end trap message


# ====================
# GAME CLASS
# ====================

class MazeGame:
    def __init__(self, maze_size=15):
        pygame.init()
        pygame.mixer.init()
        self.display = (1024, 768)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Maze - HW5 - Max Gibson")
        
        # start background music
        import os
        music_path = os.path.join(os.path.dirname(__file__), 'trippy.mp3')
        self.music_playing = True
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.30)  # low volume
            pygame.mixer.music.play(-1)  # loop forever
        except Exception as e:
            print(f"Warning: Could not load background music: {e}")
        
        # load win sound effect
        win_sound_path = os.path.join(os.path.dirname(__file__), 'win.mp3')
        try:
            self.win_sound = pygame.mixer.Sound(win_sound_path)
            self.win_sound.set_volume(0.5)  # half volume
        except Exception as e:
            print(f"Warning: Could not load win sound: {e}")
            self.win_sound = None
        
        # load scare sound effect for dead-end traps
        scare_sound_path = os.path.join(os.path.dirname(__file__), 'scare.mp3')
        try:
            self.scare_sound = pygame.mixer.Sound(scare_sound_path)
            self.scare_sound.set_volume(0.9)  # 90% volume
        except Exception as e:
            print(f"Warning: Could not load scare sound: {e}")
            self.scare_sound = None


        # hide and grab mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        # setup OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_LIGHT2)
        glEnable(GL_LIGHT3)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # ambient lighting
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.02, 0.02, 0.03, 1.0))
        
        # point lights in hallways
        for i in range(4):
            light = GL_LIGHT0 + i
            glLightfv(light, GL_AMBIENT, (0.0, 0.0, 0.0, 1))
            glLightfv(light, GL_DIFFUSE, (0.8, 0.7, 0.5, 1))
            glLightfv(light, GL_SPECULAR, (0.3, 0.25, 0.2, 1))
            # attenuation for point light falloff
            glLightf(light, GL_CONSTANT_ATTENUATION, 0.3)
            glLightf(light, GL_LINEAR_ATTENUATION, 0.5)
            glLightf(light, GL_QUADRATIC_ATTENUATION, 0.3)
        
        # enable fog for atmosphere
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, (0.02, 0.02, 0.03, 1.0))
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 2.0)
        glFogf(GL_FOG_END, 10.0)
        
        # maze setup
        self.maze_size = maze_size
        self.cell_size = 1.0
        self.wall_height = 1.0
        
        # generate initial maze
        self.maze_gen = MazeGenerator(maze_size, maze_size)
        self.maze = self.maze_gen.generate()
        
        # calculate light positions on walls
        self.light_positions = []
        self._calculate_light_positions()
        
        self.player = Player()
        # set initial player position to the start
        self.player.x = self.maze_gen.start_pos[0] + 0.5
        self.player.z = self.maze_gen.start_pos[1] + 0.5
        
        # powerups and traps
        self.powerups = []
        self.traps = []
        self._place_powerups_and_traps()
        
        # timing
        self.start_time = time.time()
        self.elapsed_time = 0
        self.game_won = False
        
        # create textures
        self._create_textures()
        
        # font for HUD
        self.font = pygame.font.SysFont('Arial', 24)
        
    def _create_textures(self):
        """create procedural textures for walls, floor, ceiling"""
        # wall texture - grimy kowloon/abandoned building style
        wall_data = []
        
        # pre-generate some noise for stains and damage
        noise = [[random.random() for _ in range(64)] for _ in range(64)]
        
        for y in range(64):
            for x in range(64):
                # base concrete/plaster color - brownish gray with slight green
                base_r = 95 + random.randint(-8, 8)
                base_g = 88 + random.randint(-8, 8)
                base_b = 80 + random.randint(-8, 8)
                
                # add water damage streaks (vertical dark lines)
                streak_chance = noise[y][x % 32]
                if streak_chance > 0.92 and y > 10:
                    darken = int(30 * (y / 64.0))
                    base_r -= darken
                    base_g -= darken
                    base_b -= darken
                
                # add mold/moisture patches (subtle greenish-brown spots)
                local_noise = noise[y % 32][(x + 17) % 64]
                if local_noise > 0.88:
                    base_r -= 10
                    base_g += 3
                    base_b -= 8
                
                # add rust stains dripping down (orange-brown)
                rust_noise = noise[(y + 23) % 64][x % 48]
                if rust_noise > 0.88 and y > 5:
                    rust_intensity = min(40, int(25 * (y / 64.0)))
                    base_r += rust_intensity
                    base_g -= 10
                    base_b -= 20
                
                # cracked/chipped areas revealing darker underlayer
                crack_noise = noise[(x * 3) % 64][(y * 2) % 64]
                if crack_noise > 0.93:
                    base_r = 50 + random.randint(-10, 10)
                    base_g = 45 + random.randint(-10, 10)
                    base_b = 40 + random.randint(-10, 10)
                
                # faded paint remnants in patches (slightly different hue)
                paint_noise = noise[(x + 11) % 64][(y + 7) % 64]
                if 0.7 < paint_noise < 0.75:
                    # faded teal/blue paint patches
                    base_r -= 10
                    base_g += 15
                    base_b += 20
                
                # horizontal water line stain
                if 40 < y < 44:
                    stain_strength = random.randint(10, 25)
                    base_r -= stain_strength
                    base_g -= stain_strength
                    base_b -= stain_strength // 2
                
                # wire/pipe shadow lines
                if (x == 12 or x == 45) and random.random() > 0.3:
                    base_r -= 25
                    base_g -= 25
                    base_b -= 20
                
                # clamp values
                r = max(20, min(255, base_r))
                g = max(20, min(255, base_g))
                b = max(20, min(255, base_b))
                
                wall_data.extend([r, g, b])
        
        self.wall_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.wall_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 64, 64, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes(wall_data))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # floor texture - stone pattern
        floor_data = []
        for y in range(64):
            for x in range(64):
                base = 80 + random.randint(-15, 15)
                if (x + y) % 32 < 2:
                    base -= 20
                floor_data.extend([base, base + 5, base + 10])
        
        self.floor_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.floor_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 64, 64, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes(floor_data))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # ceiling texture
        ceiling_data = []
        for y in range(64):
            for x in range(64):
                base = 40 + random.randint(-5, 5)
                ceiling_data.extend([base, base, base + 10])
        
        self.ceiling_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ceiling_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 64, 64, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes(ceiling_data))
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        self._load_teleport_texture()
        
        self._load_spin_texture()
        
        self._load_slow_texture()
    
    def _load_teleport_texture(self):
        """load the teleport trap wall texture from image file"""
        import os
        texture_path = os.path.join(os.path.dirname(__file__), 'allnightmask.webp')
        try:
            # Load image with pygame
            image = pygame.image.load(texture_path)
            image = pygame.transform.flip(image, False, True)
            image_data = pygame.image.tostring(image, "RGBA", True)
            width, height = image.get_size()
            
            self.teleport_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.teleport_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        except Exception as e:
            print(f"Warning: Could not load teleport texture: {e}")
            red_data = [255, 0, 0, 255] * 64 * 64
            self.teleport_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.teleport_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 64, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes(red_data))
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    def _load_spin_texture(self):
        """Load the spin trap texture from image file"""
        import os
        texture_path = os.path.join(os.path.dirname(__file__), 'swirl.jpg')
        try:
            image = pygame.image.load(texture_path)
            image = pygame.transform.flip(image, False, True)
            image_data = pygame.image.tostring(image, "RGBA", True)
            width, height = image.get_size()
            
            self.spin_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.spin_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        except Exception as e:
            print(f"Warning: Could not load spin texture: {e}")
            orange_data = [255, 128, 0, 255] * 64 * 64
            self.spin_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.spin_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 64, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes(orange_data))
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    def _load_slow_texture(self):
        """Load the slow trap texture from image file"""
        import os
        texture_path = os.path.join(os.path.dirname(__file__), 'tar.jpg')
        try:
            image = pygame.image.load(texture_path)
            image = pygame.transform.flip(image, False, True)
            image_data = pygame.image.tostring(image, "RGBA", True)
            width, height = image.get_size()
            
            self.slow_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.slow_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        except Exception as e:
            print(f"Warning: Could not load slow texture: {e}")
            purple_data = [128, 0, 128, 255] * 64 * 64
            self.slow_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.slow_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 64, 64, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes(purple_data))
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    def _place_powerups_and_traps(self):
        """Place powerups and traps in the maze"""
        self.powerups = []
        self.traps = []
        
        # get solution path and dead ends
        solution_set = set(self.maze_gen.solution_path)
        dead_ends = self.maze_gen.get_dead_ends()
        dead_ends_set = set(dead_ends)
        
        # get start and end positions to exclude (both interior and exit cells)
        start_pos = self.maze_gen.start_pos
        end_pos = self.maze_gen.end_pos
        end_exit = self.maze_gen.end_exit
        excluded_cells = {start_pos, end_pos, end_exit}
        
        # get all walkable cells (exclude start, end, and exit)
        walkable = []
        for y in range(self.maze_size):
            for x in range(self.maze_size):
                if self.maze[y][x] == 0 and (x, y) not in excluded_cells:
                    walkable.append((x, y))
        
        # place speed boosts on solution path (exclude dead ends and end position)
        solution_cells = [c for c in self.maze_gen.solution_path[2:-2] 
                         if c in solution_set and c not in dead_ends_set and c not in excluded_cells]
        if len(solution_cells) >= 2:
            for cell in random.sample(solution_cells, min(2, len(solution_cells))):
                self.powerups.append(PowerUp(cell[0] + 0.5, cell[1] + 0.5, PowerUp.SPEED_BOOST))
        
        # place jump boost off the main path (exclude dead ends and end position)
        off_path = [c for c in walkable if c not in solution_set and c not in dead_ends_set]
        if off_path:
            cell = random.choice(off_path)
            self.powerups.append(PowerUp(cell[0] + 0.5, cell[1] + 0.5, PowerUp.JUMP_BOOST))
        
        # track cells where powerups are placed to avoid placing traps there
        powerup_cells = set((int(p.x), int(p.z)) for p in self.powerups)
        
        # place traps
        # slow traps off the main path (exclude end position and powerup cells)
        off_path_no_end = [c for c in off_path if c not in powerup_cells]
        slow_trap_cells = set()
        if len(off_path_no_end) >= 3:
            slow_cells = random.sample(off_path_no_end, min(3, len(off_path_no_end)))
            for cell in slow_cells:
                self.traps.append(Trap(cell[0] + 0.5, cell[1] + 0.5, Trap.SLOW))
                slow_trap_cells.add(cell)
        
        # teleport traps at dead ends
        for cell in dead_ends:
            # 50% chance to spawn a trap at this dead end
            if random.random() > 0.73:
                continue
                
            cell_x, cell_y = cell
            
            # double check this is truly a dead end (exactly 3 walls around it)
            walls = 0
            open_direction = None
            # check each direction: (dx, dy, direction_name)
            for dx, dy, direction in [(-1, 0, 'west'), (1, 0, 'east'), (0, -1, 'north'), (0, 1, 'south')]:
                nx, ny = cell_x + dx, cell_y + dy
                if 0 <= nx < self.maze_size and 0 <= ny < self.maze_size:
                    if self.maze[ny][nx] == 1:
                        walls += 1
                    else:
                        open_direction = direction
            
            # only place trap if this is a true dead end
            if walls == 3 and open_direction is not None:
                wall_facing = open_direction
                self.traps.append(Trap(cell[0] + 0.5, cell[1] + 0.5, Trap.TELEPORT_START, wall_facing))
        
        # spin trap
        spin_candidates = [c for c in off_path_no_end if c not in dead_ends_set and c not in powerup_cells and c not in slow_trap_cells]
        if len(spin_candidates) >= 1:
            cell = random.choice(spin_candidates[:5] if len(spin_candidates) >= 5 else spin_candidates)
            self.traps.append(Trap(cell[0] + 0.5, cell[1] + 0.5, Trap.SPIN))
    
    def _calculate_light_positions(self):
        """calculate positions for wall-mounted lights in the maze"""
        self.light_positions = []
        
        # place lights on walls adjacent to corridors, spaced every 5 cells
        for z in range(1, self.maze_size - 1):
            for x in range(1, self.maze_size - 1):
                if self.maze[z][x] == 0:
                    if (x + z) % 5 == 0:
                        # find adjacent walls to mount light on
                        # check each direction for a wall
                        for dx, dz, facing in [(1, 0, 'west'), (-1, 0, 'east'), 
                                                (0, 1, 'north'), (0, -1, 'south')]:
                            wall_x, wall_z = x + dx, z + dz
                            if 0 <= wall_x < self.maze_size and 0 <= wall_z < self.maze_size:
                                if self.maze[wall_z][wall_x] == 1:
                                    # place light on this wall
                                    # light position is slightly offset from wall into corridor
                                    light_x = x + 0.5 - dx * 0.3
                                    light_z = z + 0.5 - dz * 0.3
                                    light_y = self.wall_height - 0.1
                                    self.light_positions.append((light_x, light_y, light_z, facing))
                                    break
    
    def reset_position(self):
        """reset player position and time"""
        self.player.reset()
        # set player position to the start position
        self.player.x = self.maze_gen.start_pos[0] + 0.5
        self.player.z = self.maze_gen.start_pos[1] + 0.5
        self.start_time = time.time()
        self.elapsed_time = 0
        self.game_won = False
        
        # resume music if it was paused
        if self.music_playing:
            pygame.mixer.music.unpause()
        
        # reset powerups
        for p in self.powerups:
            p.collected = False
        for t in self.traps:
            t.triggered = False
            t.cooldown = 0
    
    def regenerate_maze(self):
        """generate a new maze and reset everything"""
        self.maze = self.maze_gen.generate()
        self._calculate_light_positions()
        self._place_powerups_and_traps()
        self.reset_position()
    
    def check_collision(self, x, z, radius=0.2):
        """check if position collides with walls"""
        # check the 4 corners of the player's bounding box
        corners = [
            (x - radius, z - radius),
            (x + radius, z - radius),
            (x - radius, z + radius),
            (x + radius, z + radius)
        ]
        
        for cx, cz in corners:
            maze_x = int(cx)
            maze_z = int(cz)
            
            if maze_x < 0 or maze_x >= self.maze_size or maze_z < 0 or maze_z >= self.maze_size:
                return True
            
            if self.maze[maze_z][maze_x] == 1:
                return True
        
        return False
    
    def update(self, dt):
        """update game state"""
        if self.game_won:
            return
        
        # update elapsed time
        self.elapsed_time = time.time() - self.start_time
        
        # update player spin effect
        if self.player.spin_time > 0:
            self.player.spin_time -= dt
            self.player.yaw += self.player.spin_amount * dt
            if self.player.spin_time <= 0:
                self.player.spin_amount = 0
        
        # update jump boost
        if self.player.jump_boost_active:
            self.player.jump_time += dt
            
            # parabolic jump: up for 2 seconds, down for 2 seconds
            jump_duration = 4.0
            max_height = 8.0
            
            if self.player.jump_time < jump_duration:
                # parabola: h = max_height * (1 - ((t - duration/2) / (duration/2))^2)
                normalized = (self.player.jump_time - jump_duration / 2) / (jump_duration / 2)
                self.player.jump_height = max_height * (1 - normalized * normalized)
                self.player.y = 0.5 + self.player.jump_height
                self.player.can_move = False
            else:
                self.player.jump_boost_active = False
                self.player.jump_height = 0
                self.player.y = 0.5
                self.player.can_move = True
                self.player.jump_time = 0
                self.player.on_jump_pad = True  # Mark as on pad so it won't trigger again
        
        # update speed boost
        if self.player.speed_boost_time > 0:
            self.player.speed_boost_time -= dt
            if self.player.speed_boost_time <= 0:
                self.player.speed = self.player.base_speed
        
        # update slow debuff
        if self.player.slow_debuff_time > 0:
            self.player.slow_debuff_time -= dt
            if self.player.slow_debuff_time <= 0:
                self.player.speed = self.player.base_speed
        
        # update dead end message timer
        if self.player.dead_end_message_time > 0:
            self.player.dead_end_message_time -= dt
        
        # update powerup animations
        for powerup in self.powerups:
            powerup.rotation += dt * 90
        
        # update trap cooldowns
        for trap in self.traps:
            if trap.cooldown > 0:
                trap.cooldown -= dt
        
        # check powerup collection
        # check powerup collection and jump pad re-entry
        on_any_jump_pad = False
        for powerup in self.powerups:
            if not powerup.collected or powerup.type == PowerUp.JUMP_BOOST:
                dx = self.player.x - powerup.x
                dz = self.player.z - powerup.z
                dist_sq = dx * dx + dz * dz
                
                if powerup.type == PowerUp.JUMP_BOOST:
                    if dist_sq < 0.3:
                        on_any_jump_pad = True
                        # only trigger if not already jumping and player has re-entered
                        if not self.player.jump_boost_active and not self.player.on_jump_pad:
                            self.player.jump_boost_active = True
                            self.player.jump_time = 0
                elif powerup.type == PowerUp.SPEED_BOOST:
                    if dist_sq < 0.3:
                        powerup.collected = True
                        self.player.speed = 6.5
                        self.player.speed_boost_time = 5.0
        
        # if player is not on any jump pad, reset the flag so they can trigger again
        if not on_any_jump_pad:
            self.player.on_jump_pad = False
        
        # update regular jump physics (forward leap)
        if self.player.is_jumping:
            # vertical movement (small hop)
            self.player.jump_velocity -= self.player.gravity * dt
            self.player.y += self.player.jump_velocity * dt
            
            # forward movement during leap
            self.player.leap_time += dt
            if self.player.leap_time < self.player.leap_duration:
                # apply forward momentum with collision detection
                leap_x = self.player.x + self.player.leap_dir_x * self.player.leap_speed * dt
                leap_z = self.player.z + self.player.leap_dir_z * self.player.leap_speed * dt
                
                if not self.check_collision(leap_x, leap_z):
                    self.player.x = leap_x
                    self.player.z = leap_z
                elif not self.check_collision(leap_x, self.player.z):
                    self.player.x = leap_x
                elif not self.check_collision(self.player.x, leap_z):
                    self.player.z = leap_z
            
            # check if landed
            if self.player.y <= self.player.ground_y:
                self.player.y = self.player.ground_y
                self.player.is_jumping = False
                self.player.jump_velocity = 0
                self.player.leap_time = 0
        
        # check trap triggers - only if player is on the ground (not jumping)
        player_airborne = self.player.is_jumping or self.player.jump_boost_active
        for trap in self.traps:
            if trap.cooldown <= 0 and not player_airborne:
                dx = self.player.x - trap.x
                dz = self.player.z - trap.z
                if dx * dx + dz * dz < 0.3:
                    if trap.type == Trap.SLOW:
                        self.player.speed = self.player.base_speed * 0.3
                        self.player.speed_boost_time = 0  # cancel speed boost
                        self.player.slow_debuff_time = 5.5  # slow lasts 5.5 seconds
                        trap.cooldown = 3.0
                    elif trap.type == Trap.TELEPORT_START:
                        # verify this is a true dead end before triggering
                        cell_x, cell_z = int(trap.x), int(trap.z)
                        walls = sum(1 for ddx, ddz in [(-1,0),(1,0),(0,-1),(0,1)] 
                                   if 0 <= cell_x+ddx < self.maze_size and 0 <= cell_z+ddz < self.maze_size 
                                   and self.maze[cell_z+ddz][cell_x+ddx] == 1)
                        if walls == 3:  # only trigger at true dead ends
                            self.player.x = self.maze_gen.start_pos[0] + 0.5
                            self.player.z = self.maze_gen.start_pos[1] + 0.5
                            trap.cooldown = 5.0
                            self.player.dead_end_message_time = 3.0  # show message for 3 seconds
                            if self.scare_sound:
                                self.scare_sound.play()
                    elif trap.type == Trap.SPIN:
                        self.player.spin_time = 1.0
                        self.player.spin_amount = 360  # spin 360 degrees over 1 second
                        trap.cooldown = 5.0
        
        # check if player reached exit
        exit_x, exit_y = self.maze_gen.end_exit
        if int(self.player.x) == exit_x and int(self.player.z) == exit_y:
            if not self.game_won:
                pygame.mixer.music.pause()
                if self.win_sound:
                    self.win_sound.play()
            self.game_won = True
    
    def handle_input(self, dt):
        """Handle player input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.reset_position()
                elif event.key == pygame.K_n:
                    self.regenerate_maze()
                elif event.key == pygame.K_m:
                    # toggle music
                    if self.music_playing:
                        pygame.mixer.music.stop()
                        self.music_playing = False
                    else:
                        pygame.mixer.music.play(-1)
                        self.music_playing = True
                elif event.key == pygame.K_SPACE:
                    # regular jump (forward leap) - only if on the ground, not using jump pad, and not slowed
                    if not self.player.is_jumping and not self.player.jump_boost_active and self.player.slow_debuff_time <= 0:
                        self.player.is_jumping = True
                        self.player.jump_velocity = self.player.jump_strength
                        self.player.leap_time = 0
                        # calculate forward direction for the leap
                        yaw_rad = math.radians(self.player.yaw)
                        self.player.leap_dir_x = -math.sin(yaw_rad)
                        self.player.leap_dir_z = -math.cos(yaw_rad)
            elif event.type == pygame.MOUSEMOTION:
                dx, dy = event.rel
                self.player.yaw -= dx * 0.2
                self.player.pitch -= dy * 0.2
                self.player.pitch = max(-89, min(89, self.player.pitch))
        
        # movement
        if self.player.can_move:
            keys = pygame.key.get_pressed()
            
            move_x = 0
            move_z = 0
            
            # calculate forward and right vectors
            yaw_rad = math.radians(self.player.yaw)
            forward_x = -math.sin(yaw_rad)
            forward_z = -math.cos(yaw_rad)
            right_x = math.cos(yaw_rad)
            right_z = -math.sin(yaw_rad)
            
            if keys[pygame.K_w]:
                move_x += forward_x
                move_z += forward_z
            if keys[pygame.K_s]:
                move_x -= forward_x
                move_z -= forward_z
            if keys[pygame.K_a]:
                move_x -= right_x
                move_z -= right_z
            if keys[pygame.K_d]:
                move_x += right_x
                move_z += right_z
            
            # normalize movement
            length = math.sqrt(move_x * move_x + move_z * move_z)
            if length > 0:
                move_x /= length
                move_z /= length
                
                # apply movement with collision detection
                new_x = self.player.x + move_x * self.player.speed * dt
                new_z = self.player.z + move_z * self.player.speed * dt
                
                # try full movement
                if not self.check_collision(new_x, new_z):
                    self.player.x = new_x
                    self.player.z = new_z
                else:
                    # try sliding along walls
                    if not self.check_collision(new_x, self.player.z):
                        self.player.x = new_x
                    elif not self.check_collision(self.player.x, new_z):
                        self.player.z = new_z
        
        return True
    
    def draw_wall(self, x, y, z, width, height, depth):
        """Draw a textured wall"""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.wall_texture)
        
        glBegin(GL_QUADS)
        
        # front face
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0); glVertex3f(x, y, z + depth)
        glTexCoord2f(1, 0); glVertex3f(x + width, y, z + depth)
        glTexCoord2f(1, 1); glVertex3f(x + width, y + height, z + depth)
        glTexCoord2f(0, 1); glVertex3f(x, y + height, z + depth)
        
        # back face
        glNormal3f(0, 0, -1)
        glTexCoord2f(0, 0); glVertex3f(x + width, y, z)
        glTexCoord2f(1, 0); glVertex3f(x, y, z)
        glTexCoord2f(1, 1); glVertex3f(x, y + height, z)
        glTexCoord2f(0, 1); glVertex3f(x + width, y + height, z)
        
        # left face
        glNormal3f(-1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(x, y, z)
        glTexCoord2f(1, 0); glVertex3f(x, y, z + depth)
        glTexCoord2f(1, 1); glVertex3f(x, y + height, z + depth)
        glTexCoord2f(0, 1); glVertex3f(x, y + height, z)
        
        # right face
        glNormal3f(1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(x + width, y, z + depth)
        glTexCoord2f(1, 0); glVertex3f(x + width, y, z)
        glTexCoord2f(1, 1); glVertex3f(x + width, y + height, z)
        glTexCoord2f(0, 1); glVertex3f(x + width, y + height, z + depth)
        
        # top face
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0); glVertex3f(x, y + height, z + depth)
        glTexCoord2f(1, 0); glVertex3f(x + width, y + height, z + depth)
        glTexCoord2f(1, 1); glVertex3f(x + width, y + height, z)
        glTexCoord2f(0, 1); glVertex3f(x, y + height, z)
        
        glEnd()
        glDisable(GL_TEXTURE_2D)
    
    def draw_floor_and_ceiling(self):
        """Draw the floor and ceiling"""
        glEnable(GL_TEXTURE_2D)
        
        # floor
        glBindTexture(GL_TEXTURE_2D, self.floor_texture)
        glBegin(GL_QUADS)
        glNormal3f(0, 1, 0)
        glColor3f(0.8, 0.8, 0.8)
        for z in range(self.maze_size):
            for x in range(self.maze_size):
                if self.maze[z][x] == 0:
                    glTexCoord2f(0, 0); glVertex3f(x, 0, z)
                    glTexCoord2f(1, 0); glVertex3f(x + 1, 0, z)
                    glTexCoord2f(1, 1); glVertex3f(x + 1, 0, z + 1)
                    glTexCoord2f(0, 1); glVertex3f(x, 0, z + 1)
        glEnd()
        
        # Ceiling
        glBindTexture(GL_TEXTURE_2D, self.ceiling_texture)
        glBegin(GL_QUADS)
        glNormal3f(0, -1, 0)
        glColor3f(0.5, 0.5, 0.6)
        for z in range(self.maze_size):
            for x in range(self.maze_size):
                if self.maze[z][x] == 0:
                    glTexCoord2f(0, 0); glVertex3f(x, self.wall_height, z)
                    glTexCoord2f(0, 1); glVertex3f(x, self.wall_height, z + 1)
                    glTexCoord2f(1, 1); glVertex3f(x + 1, self.wall_height, z + 1)
                    glTexCoord2f(1, 0); glVertex3f(x + 1, self.wall_height, z)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
    
    def draw_powerup(self, powerup):
        """draw a powerup as a floating, rotating gem"""
        if powerup.collected:
            return
        
        glPushMatrix()
        glTranslatef(powerup.x, 0.3 + 0.1 * math.sin(time.time() * 2 + powerup.bob_offset), powerup.z)
        glRotatef(powerup.rotation, 0, 1, 0)
        
        glDisable(GL_LIGHTING)
        
        if powerup.type == PowerUp.SPEED_BOOST:
            glColor3f(0.0, 1.0, 0.0)  # green for speed
        else:
            glColor3f(0.0, 0.5, 1.0)  # blue for jump
        
        # draw a diamond shape
        size = 0.15
        glBegin(GL_TRIANGLES)
        # top pyramid
        for i in range(4):
            angle1 = math.radians(i * 90)
            angle2 = math.radians((i + 1) * 90)
            glVertex3f(0, size * 1.5, 0)
            glVertex3f(math.cos(angle1) * size, 0, math.sin(angle1) * size)
            glVertex3f(math.cos(angle2) * size, 0, math.sin(angle2) * size)
        # bottom pyramid
        for i in range(4):
            angle1 = math.radians(i * 90)
            angle2 = math.radians((i + 1) * 90)
            glVertex3f(0, -size * 1.5, 0)
            glVertex3f(math.cos(angle2) * size, 0, math.sin(angle2) * size)
            glVertex3f(math.cos(angle1) * size, 0, math.sin(angle1) * size)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def draw_trap(self, trap):
        """draw a trap indicator"""
        # teleport trap: draw image on the wall
        if trap.type == Trap.TELEPORT_START:
            self._draw_teleport_trap(trap)
            return
        
        # spin trap: draw textured circle on floor
        if trap.type == Trap.SPIN:
            self._draw_spin_trap(trap)
            return
        
        # slow trap: draw textured circle on floor
        glPushMatrix()
        glTranslatef(trap.x, 0.01, trap.z)
        
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.slow_texture)
        
        glColor4f(1.0, 1.0, 1.0, 1.0)  # full brightness for texture
        
        # draw a textured circle on the floor
        glBegin(GL_TRIANGLE_FAN)
        glTexCoord2f(0.5, 0.5)
        glVertex3f(0, 0, 0)
        for i in range(17):
            angle = math.radians(i * 22.5)
            # map circle edge to texture edge
            glTexCoord2f(0.5 + 0.5 * math.cos(angle), 0.5 + 0.5 * math.sin(angle))
            glVertex3f(math.cos(angle) * 0.3, 0, math.sin(angle) * 0.3)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def _draw_spin_trap(self, trap):
        """draw the spin trap with swirl texture on floor"""
        glPushMatrix()
        glTranslatef(trap.x, 0.01, trap.z)
        
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.spin_texture)
        
        glColor4f(1.0, 1.0, 1.0, 1.0)  # full brightness for texture
        
        # draw a textured circle on the floor
        glBegin(GL_TRIANGLE_FAN)
        glTexCoord2f(0.5, 0.5)  # center of texture
        glVertex3f(0, 0, 0)
        for i in range(17):
            angle = math.radians(i * 22.5)
            # map circle edge to texture edge
            glTexCoord2f(0.5 + 0.5 * math.cos(angle), 0.5 + 0.5 * math.sin(angle))
            glVertex3f(math.cos(angle) * 0.3, 0, math.sin(angle) * 0.3)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def _draw_teleport_trap(self, trap):
        """Draw the teleport trap image on the wall"""
        # only draw if we have a valid wall facing direction
        if trap.wall_facing is None:
            return
            
        # verify this is actually a dead end before drawing
        cell_x = int(trap.x)
        cell_z = int(trap.z)
        walls = 0
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, nz = cell_x + dx, cell_z + dz
            if 0 <= nx < self.maze_size and 0 <= nz < self.maze_size:
                if self.maze[nz][nx] == 1:
                    walls += 1
        
        # only draw the mask if this is a true dead end (3 walls)
        if walls != 3:
            return
        
        glPushMatrix()
        
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.teleport_texture)
        
        glColor3f(1.0, 1.0, 1.0)
        
        size = 0.4  # size of the image on wall
        height = 0.5  # center height of image
        
        glBegin(GL_QUADS)
        if trap.wall_facing == 'north':  # opening is north (smaller z), mask on SOUTH wall (larger z)
            wall_z = cell_z + 0.99  # south edge of cell (back wall)
            glTexCoord2f(0, 0); glVertex3f(cell_x + 0.5 - size, height - size, wall_z)
            glTexCoord2f(1, 0); glVertex3f(cell_x + 0.5 + size, height - size, wall_z)
            glTexCoord2f(1, 1); glVertex3f(cell_x + 0.5 + size, height + size, wall_z)
            glTexCoord2f(0, 1); glVertex3f(cell_x + 0.5 - size, height + size, wall_z)
        elif trap.wall_facing == 'south':  # opening is south (larger z), mask on NORTH wall (smaller z)
            wall_z = cell_z + 0.01  # north edge of cell (back wall)
            glTexCoord2f(1, 0); glVertex3f(cell_x + 0.5 - size, height - size, wall_z)
            glTexCoord2f(0, 0); glVertex3f(cell_x + 0.5 + size, height - size, wall_z)
            glTexCoord2f(0, 1); glVertex3f(cell_x + 0.5 + size, height + size, wall_z)
            glTexCoord2f(1, 1); glVertex3f(cell_x + 0.5 - size, height + size, wall_z)
        elif trap.wall_facing == 'west':  # opening is west (smaller x), mask on EAST wall (larger x)
            wall_x = cell_x + 0.99  # east edge of cell (back wall)
            glTexCoord2f(1, 0); glVertex3f(wall_x, height - size, cell_z + 0.5 - size)
            glTexCoord2f(0, 0); glVertex3f(wall_x, height - size, cell_z + 0.5 + size)
            glTexCoord2f(0, 1); glVertex3f(wall_x, height + size, cell_z + 0.5 + size)
            glTexCoord2f(1, 1); glVertex3f(wall_x, height + size, cell_z + 0.5 - size)
        elif trap.wall_facing == 'east':  # opening is east (larger x), mask on WEST wall (smaller x)
            wall_x = cell_x + 0.01  # west edge of cell (back wall)
            glTexCoord2f(0, 0); glVertex3f(wall_x, height - size, cell_z + 0.5 - size)
            glTexCoord2f(1, 0); glVertex3f(wall_x, height - size, cell_z + 0.5 + size)
            glTexCoord2f(1, 1); glVertex3f(wall_x, height + size, cell_z + 0.5 + size)
            glTexCoord2f(0, 1); glVertex3f(wall_x, height + size, cell_z + 0.5 - size)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def draw_light_fixture(self, x, y, z, facing):
        """Draw a wall-mounted light fixture"""
        glPushMatrix()
        glTranslatef(x, y, z)
        
        glDisable(GL_LIGHTING)
        
        # glowing light fixture
        # subtle flicker effect
        flicker = 0.9 + 0.1 * math.sin(time.time() * 10 + x * 7 + z * 11)
        glColor3f(1.0 * flicker, 0.85 * flicker, 0.5 * flicker)
        
        # draw a small glowing box/lamp
        size = 0.08
        glBegin(GL_QUADS)
        # bottom (glowing part)
        glVertex3f(-size, -size * 0.5, -size)
        glVertex3f(size, -size * 0.5, -size)
        glVertex3f(size, -size * 0.5, size)
        glVertex3f(-size, -size * 0.5, size)
        
        # sides
        glVertex3f(-size, 0, -size)
        glVertex3f(-size, -size * 0.5, -size)
        glVertex3f(-size, -size * 0.5, size)
        glVertex3f(-size, 0, size)
        
        glVertex3f(size, 0, -size)
        glVertex3f(size, -size * 0.5, -size)
        glVertex3f(size, -size * 0.5, size)
        glVertex3f(size, 0, size)
        
        glVertex3f(-size, 0, -size)
        glVertex3f(size, 0, -size)
        glVertex3f(size, -size * 0.5, -size)
        glVertex3f(-size, -size * 0.5, -size)
        
        glVertex3f(-size, 0, size)
        glVertex3f(size, 0, size)
        glVertex3f(size, -size * 0.5, size)
        glVertex3f(-size, -size * 0.5, size)
        glEnd()
        
        # draw a glow effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glColor4f(1.0, 0.8, 0.4, 0.4 * flicker)
        
        # glow halo
        glow_size = 0.2
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, -size * 0.5, 0)
        for i in range(9):
            angle = math.radians(i * 45)
            glVertex3f(math.cos(angle) * glow_size, -size * 0.5 - 0.05, math.sin(angle) * glow_size)
        glEnd()
        
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def draw_exit(self):
        """draw the exit marker"""
        exit_x = self.maze_gen.end_exit[0] + 0.5
        exit_z = self.maze_gen.end_exit[1] + 0.5
        
        glPushMatrix()
        glTranslatef(exit_x, 0.5, exit_z)
        
        glDisable(GL_LIGHTING)
        
        # pulsing golden glow
        pulse = 0.5 + 0.5 * math.sin(time.time() * 3)
        glColor3f(1.0, 0.8 * pulse + 0.2, 0.0)
        
        # draw a simple beacon
        glBegin(GL_LINES)
        for i in range(8):
            angle = math.radians(i * 45 + time.time() * 50)
            glVertex3f(0, -0.3, 0)
            glVertex3f(math.cos(angle) * 0.3, 0.5, math.sin(angle) * 0.3)
        glEnd()
        
        # draw yellow diamond above exit only when player is using jump pad
        if self.player.jump_boost_active:
            glColor3f(1.0, 1.0, 0.0)  # bright yellow
            size = 0.3
            # diamond floats high above the exit
            diamond_height = 2
            glBegin(GL_TRIANGLES)
            # top pyramid
            for i in range(4):
                angle1 = math.radians(i * 90)
                angle2 = math.radians((i + 1) * 90)
                glVertex3f(0, diamond_height + size * 1.5, 0)
                glVertex3f(math.cos(angle1) * size, diamond_height, math.sin(angle1) * size)
                glVertex3f(math.cos(angle2) * size, diamond_height, math.sin(angle2) * size)
            # bottom pyramid
            for i in range(4):
                angle1 = math.radians(i * 90)
                angle2 = math.radians((i + 1) * 90)
                glVertex3f(0, diamond_height - size * 1.5, 0)
                glVertex3f(math.cos(angle2) * size, diamond_height, math.sin(angle2) * size)
                glVertex3f(math.cos(angle1) * size, diamond_height, math.sin(angle1) * size)
            glEnd()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def draw_hud(self):
        """Draw the HUD overlay"""
        # switch to 2D rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.display[0], self.display[1], 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_FOG)
        
        # Create text surfaces
        time_text = f"Time: {self.elapsed_time:.1f}s"
        pos_text = f"Pos: ({self.player.x:.1f}, {self.player.z:.1f})"
        
        # Status effects
        status = []
        if self.player.speed_boost_time > 0:
            status.append(f"SPEED BOOST: {self.player.speed_boost_time:.1f}s")
        if self.player.jump_boost_active:
            status.append("JUMPING - LOOK AROUND!")
        if self.player.slow_debuff_time > 0:
            status.append(f"SLOWED: {self.player.slow_debuff_time:.1f}s")
        if self.player.dead_end_message_time > 0:
            status.append("Muahahah! Dead end, try again...")
        
        # Render text as textures
        self._render_text(time_text, 10, 10, (255, 255, 255))
        self._render_text(pos_text, 10, 40, (255, 255, 255))
        
        y_offset = 70
        for s in status:
            if "Muahahah" in s:
                color = (255, 0, 0)  # red for dead end message
            elif "BOOST" in s or "JUMPING" in s:
                color = (0, 255, 0)
            else:
                color = (255, 100, 100)
            self._render_text(s, 10, y_offset, color)
            y_offset += 30
        
        if self.game_won:
            self._render_text(f"YOU WIN! Time: {self.elapsed_time:.2f}s", 
                            self.display[0] // 2 - 100, self.display[1] // 2, (255, 215, 0))
            self._render_text("Press R to restart or N for new maze", 
                            self.display[0] // 2 - 150, self.display[1] // 2 + 40, (255, 255, 255))
        
        # Controls help at bottom
        self._render_text("W/A/S/D: Move | Mouse: Look | R: Reset | N: New Maze | M: Music | ESC: Quit", 
                         10, self.display[1] - 30, (200, 200, 200))
        
        glEnable(GL_FOG)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def _render_text(self, text, x, y, color):
        """Render text at position using pygame and OpenGL textures"""
        # Render text to a pygame surface
        text_surface = self.font.render(text, True, color, (0, 0, 0))
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        
        # Convert to a format OpenGL can use (power of 2 not required for modern OpenGL)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        
        # Create texture
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_width, text_height, 0, 
                     GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        # Draw textured quad
        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + text_width, y)
        glTexCoord2f(1, 0); glVertex2f(x + text_width, y + text_height)
        glTexCoord2f(0, 0); glVertex2f(x, y + text_height)
        glEnd()
        
        # Clean up
        glDeleteTextures([texture])
        glDisable(GL_BLEND)
        glDisable(GL_TEXTURE_2D)
    
    def render(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.02, 0.02, 0.03, 1.0)  # Very dark background
        
        # Setup perspective
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(70, self.display[0] / self.display[1], 0.1, 100)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Camera
        yaw_rad = math.radians(self.player.yaw)
        pitch_rad = math.radians(self.player.pitch)
        
        look_x = -math.sin(yaw_rad) * math.cos(pitch_rad)
        look_y = math.sin(pitch_rad)
        look_z = -math.cos(yaw_rad) * math.cos(pitch_rad)
        
        gluLookAt(
            self.player.x, self.player.y, self.player.z,
            self.player.x + look_x, self.player.y + look_y, self.player.z + look_z,
            0, 1, 0
        )
        
        # Check if player is jumping - if so, illuminate entire maze
        if self.player.jump_boost_active:
            # Bright ambient lighting to see the whole maze
            glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.6, 0.6, 0.7, 1.0))
            # Disable fog so we can see far
            glDisable(GL_FOG)
            # Set all 4 lights to bright directional light from above
            for i in range(4):
                light = GL_LIGHT0 + i
                glLightfv(light, GL_DIFFUSE, (0.5, 0.5, 0.6, 1))
                glLightfv(light, GL_POSITION, (self.maze_size / 2, 20, self.maze_size / 2, 1.0))
                glLightf(light, GL_CONSTANT_ATTENUATION, 1.0)
                glLightf(light, GL_LINEAR_ATTENUATION, 0.0)
                glLightf(light, GL_QUADRATIC_ATTENUATION, 0.0)
        else:
            # Normal dark lighting - restore settings
            glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.02, 0.02, 0.03, 1.0))
            glEnable(GL_FOG)
            # Restore point light attenuation
            for i in range(4):
                light = GL_LIGHT0 + i
                glLightfv(light, GL_DIFFUSE, (0.8, 0.7, 0.5, 1))
                glLightf(light, GL_CONSTANT_ATTENUATION, 0.3)
                glLightf(light, GL_LINEAR_ATTENUATION, 0.5)
                glLightf(light, GL_QUADRATIC_ATTENUATION, 0.3)
            
            # Find the 4 closest lights to the player and position OpenGL lights there
            lights_with_dist = []
            for lx, ly, lz, facing in self.light_positions:
                dist = (lx - self.player.x) ** 2 + (lz - self.player.z) ** 2
                lights_with_dist.append((dist, lx, ly, lz, facing))
            
            # Sort by distance and take closest 4
            lights_with_dist.sort(key=lambda x: x[0])
            closest_lights = lights_with_dist[:4]
            
            # Position OpenGL lights at the closest light fixtures
            for i, (dist, lx, ly, lz, facing) in enumerate(closest_lights):
                light = GL_LIGHT0 + i
                glLightfv(light, GL_POSITION, (lx, ly, lz, 1.0))
            
            # Disable unused lights if fewer than 4 nearby
            for i in range(len(closest_lights), 4):
                light = GL_LIGHT0 + i
                glLightfv(light, GL_POSITION, (0, -100, 0, 1.0))  # Move far away
        
        # Draw floor and ceiling
        self.draw_floor_and_ceiling()
        
        # Draw walls
        glColor3f(1.0, 1.0, 1.0)
        for z in range(self.maze_size):
            for x in range(self.maze_size):
                if self.maze[z][x] == 1:
                    self.draw_wall(x, 0, z, self.cell_size, self.wall_height, self.cell_size)
        
        # Draw all light fixtures
        for lx, ly, lz, facing in self.light_positions:
            self.draw_light_fixture(lx, ly, lz, facing)
        
        # Draw powerups
        for powerup in self.powerups:
            self.draw_powerup(powerup)
        
        # Draw traps
        for trap in self.traps:
            self.draw_trap(trap)
        
        # Draw exit
        self.draw_exit()
        
        # Draw HUD
        self.draw_hud()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0
            
            running = self.handle_input(dt)
            self.update(dt)
            self.render()
        
        pygame.quit()


# ====================
# MAIN
# ====================

if __name__ == "__main__":
    game = MazeGame(maze_size=15)
    game.run()

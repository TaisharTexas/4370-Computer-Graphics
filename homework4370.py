import pygame
import random
import math
import time
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
MAZE_SIZE = 10
CELL_SIZE = 64
WALL_HEIGHT = 100
PLAYER_HEIGHT = 50
PLAYER_SPEED = 3
MOUSE_SENSITIVITY = 0.2
FOV = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("3D Maze Game")
clock = pygame.time.Clock()

# Generate a better random maze using Prim's algorithm
def generate_maze(size):
    # Initialize maze with walls (1 = wall, 0 = path)
    maze = [[1 for _ in range(size)] for _ in range(size)]
    
    # Start from the center
    start_x, start_y = size // 2, size // 2
    maze[start_y][start_x] = 0
    
    # List of frontier cells
    frontiers = []
    
    # Add initial frontiers
    for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
        nx, ny = start_x + dx, start_y + dy
        if 0 < nx < size-1 and 0 < ny < size-1:
            frontiers.append((nx, ny, start_x, start_y))
    
    while frontiers:
        # Choose a random frontier cell
        fx, fy, px, py = frontiers.pop(random.randint(0, len(frontiers)-1))
        
        if maze[fy][fx] == 1:  # If it's still a wall
            # Connect to the parent cell
            maze[fy][fx] = 0
            maze[(fy + py) // 2][(fx + px) // 2] = 0
            
            # Add new frontiers
            for dx, dy in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                nx, ny = fx + dx, fy + dy
                if 0 < nx < size-1 and 0 < ny < size-1 and maze[ny][nx] == 1:
                    frontiers.append((nx, ny, fx, fy))
    
    # Ensure entrance and exit are clear
    maze[1][0] = 0  # Entrance
    maze[1][1] = 0
    maze[size-2][size-1] = 0  # Exit
    maze[size-2][size-2] = 0
    
    # Add traps, power-ups, and specials
    empty_cells = []
    for y in range(size):
        for x in range(size):
            if maze[y][x] == 0 and (x, y) != (0, 1) and (x, y) != (size-1, size-2):
                empty_cells.append((x, y))
    
    # Add fewer special items to keep paths clear
    num_specials = min(len(empty_cells) // 8, 10)
    for _ in range(num_specials):
        if empty_cells:
            x, y = random.choice(empty_cells)
            empty_cells.remove((x, y))
            if random.random() < 0.4:
                maze[y][x] = 2  # Trap
            elif random.random() < 0.7:
                maze[y][x] = 3  # Power-up
            else:
                maze[y][x] = 4  # Special
    
    return maze

# Player class with improved collision detection
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.strafe_speed = PLAYER_SPEED * 0.7
        self.is_flying = False
        self.fly_timer = 0
        self.has_powerup = False
        self.powerup_timer = 0
        self.hint_charges = 3
        self.last_hint_time = 0
        self.hint_cooldown = 5  # seconds
        self.radius = CELL_SIZE // 4  # Collision radius
    
    def move(self, dx, dy, maze):
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check collisions with all nearby cells
        player_cell_x = int(new_x / CELL_SIZE)
        player_cell_y = int(new_y / CELL_SIZE)
        
        # Check 3x3 area around player for collisions
        for check_y in range(player_cell_y - 1, player_cell_y + 2):
            for check_x in range(player_cell_x - 1, player_cell_x + 2):
                if 0 <= check_x < MAZE_SIZE and 0 <= check_y < MAZE_SIZE:
                    if maze[check_y][check_x] == 1:  # Wall
                        # Calculate cell boundaries
                        cell_left = check_x * CELL_SIZE
                        cell_right = (check_x + 1) * CELL_SIZE
                        cell_top = check_y * CELL_SIZE
                        cell_bottom = (check_y + 1) * CELL_SIZE
                        
                        # Check if player would collide with this wall
                        if (new_x + self.radius > cell_left and 
                            new_x - self.radius < cell_right and 
                            new_y + self.radius > cell_top and 
                            new_y - self.radius < cell_bottom):
                            
                            # Collision detected, don't move
                            return False
        
        # No collisions, update position
        self.x = new_x
        self.y = new_y
        return True
    
    def rotate(self, angle):
        self.angle = (self.angle + angle) % 360
    
    def update(self, maze):
        # Update flying state
        if self.is_flying:
            self.fly_timer -= 1/60
            if self.fly_timer <= 0:
                self.is_flying = False
                self.height = PLAYER_HEIGHT
        
        # Update power-up state
        if self.has_powerup:
            self.powerup_timer -= 1/60
            if self.powerup_timer <= 0:
                self.has_powerup = False
                self.speed = PLAYER_SPEED
        
        # Check for special cells
        cell_x, cell_y = int(self.x / CELL_SIZE), int(self.y / CELL_SIZE)
        
        # Ensure we're within maze bounds before checking cell type
        if 0 <= cell_x < MAZE_SIZE and 0 <= cell_y < MAZE_SIZE:
            cell_type = maze[cell_y][cell_x]
            
            if cell_type == 2:  # Trap
                # Slow down player temporarily (only while on trap)
                pass  # We'll handle this in movement
                
            elif cell_type == 3:  # Power-up
                # Speed up player
                self.speed = PLAYER_SPEED * 1.5
                self.has_powerup = True
                self.powerup_timer = 10  # 10 seconds
                # Reset the cell so it's not triggered again
                maze[cell_y][cell_x] = 0
                
            elif cell_type == 4:  # Special
                # Random special effect
                effect = random.randint(1, 3)
                if effect == 1:  # Reset to start
                    self.x = CELL_SIZE * 1 + CELL_SIZE // 2
                    self.y = CELL_SIZE * 1 + CELL_SIZE // 2
                elif effect == 2:  # Turn 90 degrees
                    self.rotate(90)
                elif effect == 3:  # Launch player to fly
                    self.is_flying = True
                    self.fly_timer = 3  # 3 seconds
                    self.height = WALL_HEIGHT * 2
                # Reset the cell so it's not triggered again
                maze[cell_y][cell_x] = 0

# Improved raycasting for 3D rendering
def cast_ray(player, angle, maze):
    # Convert angle to radians
    rad = math.radians(angle)
    
    # Player position in grid coordinates
    px, py = player.x / CELL_SIZE, player.y / CELL_SIZE
    
    # Ray direction
    ray_dir_x = math.cos(rad)
    ray_dir_y = math.sin(rad)
    
    # Length of ray from current position to next x or y-side
    delta_dist_x = abs(1 / ray_dir_x) if ray_dir_x != 0 else float('inf')
    delta_dist_y = abs(1 / ray_dir_y) if ray_dir_y != 0 else float('inf')
    
    # Direction to step in x or y direction (either +1 or -1)
    step_x = 1 if ray_dir_x >= 0 else -1
    step_y = 1 if ray_dir_y >= 0 else -1
    
    # Length of ray from one x or y-side to next x or y-side
    side_dist_x = (math.ceil(px) - px) * delta_dist_x if ray_dir_x >= 0 else (px - math.floor(px)) * delta_dist_x
    side_dist_y = (math.ceil(py) - py) * delta_dist_y if ray_dir_y >= 0 else (py - math.floor(py)) * delta_dist_y
    
    # Current map position
    map_x, map_y = int(px), int(py)
    
    # Perform DDA (Digital Differential Analysis)
    hit = 0  # Was a wall hit?
    side = 0  # Was a NS or a EW wall hit?
    
    max_steps = 20  # Prevent infinite loops
    
    while hit == 0 and max_steps > 0:
        max_steps -= 1
        
        # Jump to next map square, either in x-direction, or in y-direction
        if side_dist_x < side_dist_y:
            side_dist_x += delta_dist_x
            map_x += step_x
            side = 0
        else:
            side_dist_y += delta_dist_y
            map_y += step_y
            side = 1
        
        # Check if ray has hit a wall or gone out of bounds
        if map_x < 0 or map_x >= MAZE_SIZE or map_y < 0 or map_y >= MAZE_SIZE:
            hit = 1
            break
            
        if maze[map_y][map_x] == 1:  # Wall
            hit = 1
    
    # Calculate distance projected on camera direction
    if side == 0:
        perp_wall_dist = (map_x - px + (1 - step_x) / 2) / ray_dir_x
    else:
        perp_wall_dist = (map_y - py + (1 - step_y) / 2) / ray_dir_y
    
    # Prevent division by zero
    if perp_wall_dist <= 0:
        perp_wall_dist = 0.001
    
    # Calculate height of line to draw on screen
    line_height = int(SCREEN_HEIGHT / perp_wall_dist)
    
    # Calculate lowest and highest pixel to fill in current stripe
    draw_start = max(-line_height // 2 + SCREEN_HEIGHT // 2, 0)
    draw_end = min(line_height // 2 + SCREEN_HEIGHT // 2, SCREEN_HEIGHT)
    
    # Return wall distance and side for shading
    cell_type = maze[map_y][map_x] if 0 <= map_y < MAZE_SIZE and 0 <= map_x < MAZE_SIZE else 1
    return perp_wall_dist, side, map_x, map_y, cell_type

# Render the 3D scene
def render_scene(player, maze):
    # Clear the screen
    screen.fill(BLACK)
    
    # Draw ceiling
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    
    # Draw floor
    pygame.draw.rect(screen, (80, 80, 80), (0, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
    
    # Raycast for each vertical strip
    for x in range(SCREEN_WIDTH):
        # Calculate ray position and direction
        camera_x = 2 * x / SCREEN_WIDTH - 1  # x-coordinate in camera space
        ray_angle = player.angle + math.degrees(math.atan(camera_x * math.tan(math.radians(FOV / 2))))
        
        # Cast ray
        wall_dist, side, map_x, map_y, cell_type = cast_ray(player, ray_angle, maze)
        
        # Calculate line height
        line_height = int(SCREEN_HEIGHT / wall_dist) if wall_dist > 0 else SCREEN_HEIGHT
        
        # Calculate lowest and highest pixel to fill in current stripe
        draw_start = max(-line_height // 2 + SCREEN_HEIGHT // 2, 0)
        draw_end = min(line_height // 2 + SCREEN_HEIGHT // 2, SCREEN_HEIGHT)
        
        # Choose wall color based on cell type and side
        if cell_type == 1:  # Regular wall
            color = DARK_GRAY if side == 1 else GRAY
        elif cell_type == 2:  # Trap
            color = (200, 0, 0) if side == 1 else (150, 0, 0)
        elif cell_type == 3:  # Power-up
            color = (0, 200, 0) if side == 1 else (0, 150, 0)
        elif cell_type == 4:  # Special
            color = (0, 0, 200) if side == 1 else (0, 0, 150)
        else:  # Default to wall color
            color = DARK_GRAY if side == 1 else GRAY
        
        # Draw the walls
        pygame.draw.line(screen, color, (x, draw_start), (x, draw_end), 1)
    
    # Draw minimap in the corner
    minimap_size = 150
    cell_size_minimap = minimap_size // MAZE_SIZE
    
    # Draw minimap background
    pygame.draw.rect(screen, (40, 40, 40), (10, 10, minimap_size, minimap_size))
    
    # Draw maze on minimap
    for y in range(MAZE_SIZE):
        for x in range(MAZE_SIZE):
            rect = pygame.Rect(10 + x * cell_size_minimap, 10 + y * cell_size_minimap, 
                              cell_size_minimap, cell_size_minimap)
            
            if maze[y][x] == 1:  # Wall
                pygame.draw.rect(screen, WHITE, rect)
            elif maze[y][x] == 2:  # Trap
                pygame.draw.rect(screen, RED, rect)
            elif maze[y][x] == 3:  # Power-up
                pygame.draw.rect(screen, GREEN, rect)
            elif maze[y][x] == 4:  # Special
                pygame.draw.rect(screen, BLUE, rect)
            else:  # Path
                pygame.draw.rect(screen, BLACK, rect)
    
    # Draw player on minimap
    player_x_minimap = 10 + int(player.x / CELL_SIZE * cell_size_minimap)
    player_y_minimap = 10 + int(player.y / CELL_SIZE * cell_size_minimap)
    pygame.draw.circle(screen, YELLOW, (player_x_minimap, player_y_minimap), 3)
    
    # Draw player direction line on minimap
    direction_length = 10
    end_x = player_x_minimap + direction_length * math.cos(math.radians(player.angle))
    end_y = player_y_minimap + direction_length * math.sin(math.radians(player.angle))
    pygame.draw.line(screen, YELLOW, (player_x_minimap, player_y_minimap), (end_x, end_y), 2)

# Display HUD with time and position
def display_hud(player, start_time, maze_completed):
    # Calculate elapsed time
    if not maze_completed:
        elapsed_time = time.time() - start_time
    else:
        elapsed_time = completion_time
    
    # Format time as minutes:seconds
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    time_text = f"Time: {minutes:02d}:{seconds:02d}"
    
    # Display time
    font = pygame.font.SysFont(None, 36)
    time_surface = font.render(time_text, True, WHITE)
    screen.blit(time_surface, (SCREEN_WIDTH - time_surface.get_width() - 10, 10))
    
    # Display position
    pos_text = f"Position: ({int(player.x / CELL_SIZE)}, {int(player.y / CELL_SIZE)})"
    pos_surface = font.render(pos_text, True, WHITE)
    screen.blit(pos_surface, (SCREEN_WIDTH - pos_surface.get_width() - 10, 50))
    
    # Display hint charges
    hint_text = f"Hints: {player.hint_charges}"
    hint_surface = font.render(hint_text, True, WHITE)
    screen.blit(hint_surface, (10, SCREEN_HEIGHT - 40))
    
    # Display power-up status
    if player.has_powerup:
        powerup_text = f"Speed Boost: {int(player.powerup_timer)}s"
        powerup_surface = font.render(powerup_text, True, GREEN)
        screen.blit(powerup_surface, (SCREEN_WIDTH - powerup_surface.get_width() - 10, 90))
    
    # Display flying status
    if player.is_flying:
        fly_text = f"Flying: {int(player.fly_timer)}s"
        fly_surface = font.render(fly_text, True, BLUE)
        screen.blit(fly_surface, (SCREEN_WIDTH - fly_surface.get_width() - 10, 130))
    
    # Display instructions
    instructions = [
        "WASD: Move",
        "Mouse: Look",
        "R: Reset position",
        "N: New maze",
        "H: Use hint (limited)",
        "ESC: Quit"
    ]
    
    for i, instruction in enumerate(instructions):
        instr_surface = pygame.font.SysFont(None, 24).render(instruction, True, WHITE)
        screen.blit(instr_surface, (10, 180 + i * 25))

# Display completion message
def display_completion():
    font = pygame.font.SysFont(None, 72)
    text = font.render("MAZE COMPLETED!", True, GREEN)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    
    # Display completion time
    time_font = pygame.font.SysFont(None, 36)
    minutes = int(completion_time // 60)
    seconds = int(completion_time % 60)
    time_text = f"Time: {minutes:02d}:{seconds:02d}"
    time_surface = time_font.render(time_text, True, WHITE)
    time_rect = time_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(time_surface, time_rect)

# Show hint (highlight path to exit)
def show_hint(player, maze):
    if player.hint_charges > 0 and time.time() - player.last_hint_time > player.hint_cooldown:
        player.hint_charges -= 1
        player.last_hint_time = time.time()
        
        # Simple BFS to find path to exit
        start = (int(player.x / CELL_SIZE), int(player.y / CELL_SIZE))
        exit_pos = (MAZE_SIZE-1, MAZE_SIZE-2)
        
        queue = [start]
        visited = {start: None}
        
        while queue:
            current = queue.pop(0)
            
            if current == exit_pos:
                break
                
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if (0 <= neighbor[0] < MAZE_SIZE and 0 <= neighbor[1] < MAZE_SIZE and 
                    maze[neighbor[1]][neighbor[0]] != 1 and neighbor not in visited):
                    queue.append(neighbor)
                    visited[neighbor] = current
        
        # Reconstruct path
        path = []
        current = exit_pos
        
        while current in visited and visited[current] is not None:
            path.append(current)
            current = visited[current]
        
        # Draw path on minimap
        minimap_size = 150
        cell_size_minimap = minimap_size // MAZE_SIZE
        
        for pos in path:
            x, y = pos
            if 0 <= x < MAZE_SIZE and 0 <= y < MAZE_SIZE:  # Safety check
                rect = pygame.Rect(10 + x * cell_size_minimap, 10 + y * cell_size_minimap, 
                                  cell_size_minimap, cell_size_minimap)
                pygame.draw.rect(screen, YELLOW, rect, 1)
        
        return True
    return False

# Main game function
def main():
    global completion_time
    
    # Generate initial maze
    maze = generate_maze(MAZE_SIZE)
    
    # Create player at entrance - start in a clear area
    player = Player(CELL_SIZE * 1 + CELL_SIZE // 2, CELL_SIZE * 1 + CELL_SIZE // 2)
    
    # Game state
    running = True
    maze_completed = False
    start_time = time.time()
    completion_time = 0
    
    # Hide mouse cursor
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:  # Reset position
                    player.x = CELL_SIZE * 1 + CELL_SIZE // 2
                    player.y = CELL_SIZE * 1 + CELL_SIZE // 2
                    player.angle = 0
                    start_time = time.time()
                    maze_completed = False
                elif event.key == pygame.K_n:  # New maze
                    maze = generate_maze(MAZE_SIZE)
                    player.x = CELL_SIZE * 1 + CELL_SIZE // 2
                    player.y = CELL_SIZE * 1 + CELL_SIZE // 2
                    player.angle = 0
                    start_time = time.time()
                    maze_completed = False
                    player.hint_charges = 3
                elif event.key == pygame.K_h:  # Use hint
                    show_hint(player, maze)
            
            elif event.type == pygame.MOUSEMOTION:
                # Mouse look
                dx, dy = event.rel
                player.rotate(dx * MOUSE_SENSITIVITY)
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        
        # Movement
        move_x, move_y = 0, 0
        
        # Check if player is on a trap (slow movement)
        current_speed = player.speed
        cell_x, cell_y = int(player.x / CELL_SIZE), int(player.y / CELL_SIZE)
        if 0 <= cell_x < MAZE_SIZE and 0 <= cell_y < MAZE_SIZE and maze[cell_y][cell_x] == 2:
            current_speed = player.speed * 0.5  # Slow down on traps
        
        # Forward/backward movement
        if keys[pygame.K_w]:
            move_x += math.cos(math.radians(player.angle)) * current_speed
            move_y += math.sin(math.radians(player.angle)) * current_speed
        if keys[pygame.K_s]:
            move_x -= math.cos(math.radians(player.angle)) * current_speed
            move_y -= math.sin(math.radians(player.angle)) * current_speed
        
        # Strafe movement
        if keys[pygame.K_a]:
            move_x += math.cos(math.radians(player.angle - 90)) * player.strafe_speed
            move_y += math.sin(math.radians(player.angle - 90)) * player.strafe_speed
        if keys[pygame.K_d]:
            move_x += math.cos(math.radians(player.angle + 90)) * player.strafe_speed
            move_y += math.sin(math.radians(player.angle + 90)) * player.strafe_speed
        
        # Apply movement
        if move_x != 0 or move_y != 0:
            player.move(move_x, move_y, maze)
        
        # Update player state
        player.update(maze)
        
        # Check if player reached the exit
        if (int(player.x / CELL_SIZE) == MAZE_SIZE-1 and 
            int(player.y / CELL_SIZE) == MAZE_SIZE-2 and not maze_completed):
            maze_completed = True
            completion_time = time.time() - start_time
        
        # Render the scene
        render_scene(player, maze)
        
        # Display HUD
        display_hud(player, start_time, maze_completed)
        
        # Display completion message if maze is completed
        if maze_completed:
            display_completion()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
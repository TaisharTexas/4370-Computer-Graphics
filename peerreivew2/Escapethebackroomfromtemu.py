import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math
import random
import time

normals = (
    (0, 0, -1),  # front
    (0, 1, 0),   # top
    (0, 0, 1),   # back
    (0, -1, 0),  # bottom
    (1, 0, 0),   # right
    (-1, 0, 0),  # left
)


def verts(x, y, z, n):
    vertices = (
        (1 + (2 * x), -1 + (2 * y), -1 + (2 * z)),
        (1 + (2 * x), 1 + (2 * y), -1 + (2 * z)),
        (-1 + (2 * x), 1 + (2 * y), -1 + (2 * z)),
        (-1 + (2 * x), -1 + (2 * y), -1 + (2 * z)),
        (1 + (2 * x), -1 + (2 * y), 1 + (2 * z)),
        (1 + (2 * x), 1 + (2 * y), 1 + (2 * z)),
        (-1 + (2 * x), -1 + (2 * y), 1 + (2 * z)),
        (-1 + (2 * x), 1 + (2 * y), 1 + (2 * z))
    )
    return vertices

edges = ((0,1), (0,3), (0,4), (2,1), (2,3), (2,7), (6,3), (6,4),
         (6,7), (5,1), (5,4), (5,7))

texture_coords = [
    ((0, 0), (1, 0), (1, 1), (0, 1)),  # front
    ((0, 0), (1, 0), (1, 1), (0, 1)),  # back
    ((0, 0), (1, 0), (1, 1), (0, 1)),  # left
    ((0, 0), (1, 0), (1, 1), (0, 1)),  # right
    ((0, 0), (1, 0), (1, 1), (0, 1)),  # top
    ((0, 0), (1, 0), (1, 1), (0, 1)),  # bottom
]

surfaces = ((0,1,2,3), (3,2,7,6), (4,0,3,6), (1,5,7,2) ,  (4,5,1,0), (6,7,5,4))

def Cube(vx, vy, vz, texture, texID):
    glBindTexture(GL_TEXTURE_2D, texID)
    
    vertices = verts(vx, vy, vz, 0)
    
    glColor3f(1.0, 1.0, 1.0)  # ensure texture is fully visible
    glBegin(GL_QUADS)
    for surface_index, surface in enumerate(surfaces):
        glNormal3fv(normals[surface_index])
        for vertex_index, vertex in enumerate(surface):
            glTexCoord2fv(texture[surface_index][vertex_index])
            glVertex3fv(vertices[vertex])
    glEnd()
    
    # optional edges
    glColor3f(0, 0, 0)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()
    
def CubeFloor(vx, vy, vz, texture, texID):
    glBindTexture(GL_TEXTURE_2D, texID)
    vertices = verts(vx, vy, vz, 0)

    # Only draw the bottom face
    bottom_surface = (6,7,5,4)
    glColor3f(1.0, 1.0, 1.0)  # ensure texture shows
    glBegin(GL_QUADS)
    glNormal3fv(normals[3])  # bottom normal
    for i, vertex in enumerate(bottom_surface):
        glTexCoord2fv(texture[3][i])  # use bottom face texture coords
        glVertex3fv(vertices[vertex])
    glEnd()

def Cuberoof(vx, vy, vz, texture, texID):
    glBindTexture(GL_TEXTURE_2D, texID)
    vertices = verts(vx, vy, vz, 0)

    # Only draw the bottom face
    bottom_surface = (0,1,2,3)
    glColor3f(1.0, 1.0, 1.0)  # ensure texture shows
    glBegin(GL_QUADS)
    glNormal3fv(normals[3])  # bottom normal
    for i, vertex in enumerate(bottom_surface):
        glTexCoord2fv(texture[3][i])  # use bottom face texture coords
        glVertex3fv(vertices[vertex])
    glEnd()

class BoundingBox:
    def __init__(self, min_x, max_x, min_y, max_y, min_z, max_z):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.min_z = min_z
        self.max_z = max_z

    def intersects(self, other):
        return (self.min_x <= other.max_x and self.max_x >= other.min_x and
                self.min_y <= other.max_y and self.max_y >= other.min_y and
                self.min_z <= other.max_z and self.max_z >= other.min_z)

    def draw(self):
        glBegin(GL_LINES)

        glVertex3f(self.min_x, self.min_y, self.min_z); glVertex3f(self.max_x, self.min_y, self.min_z)
        glVertex3f(self.max_x, self.min_y, self.min_z); glVertex3f(self.max_x, self.max_y, self.min_z)
        glVertex3f(self.max_x, self.max_y, self.min_z); glVertex3f(self.min_x, self.max_y, self.min_z)
        glVertex3f(self.min_x, self.max_y, self.min_z); glVertex3f(self.min_x, self.min_y, self.min_z)

        glVertex3f(self.min_x, self.min_y, self.max_z); glVertex3f(self.max_x, self.min_y, self.max_z)
        glVertex3f(self.max_x, self.min_y, self.max_z); glVertex3f(self.max_x, self.max_y, self.max_z)
        glVertex3f(self.max_x, self.max_y, self.max_z); glVertex3f(self.min_x, self.max_y, self.max_z)
        glVertex3f(self.min_x, self.max_y, self.max_z); glVertex3f(self.min_x, self.min_y, self.max_z)

        glVertex3f(self.min_x, self.min_y, self.min_z); glVertex3f(self.min_x, self.min_y, self.max_z)
        glVertex3f(self.max_x, self.min_y, self.min_z); glVertex3f(self.max_x, self.min_y, self.max_z)
        glVertex3f(self.max_x, self.max_y, self.min_z); glVertex3f(self.max_x, self.max_y, self.max_z)
        glVertex3f(self.min_x, self.max_y, self.min_z); glVertex3f(self.min_x, self.max_y, self.max_z)
        glEnd()

def create_cube_bbox(vx, vy, vz):

    min_x = -1 + (2 * vx)
    max_x = 1 + (2 * vx)
    min_y = -1 + (2 * vy)
    max_y = 1 + (2 * vy)
    min_z = -1 + (2 * vz)
    max_z = 1 + (2 * vz)
    return BoundingBox(min_x, max_x, min_y, max_y, min_z, max_z)

pygame.init()
display = (1000, 1000)
screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glShadeModel(GL_SMOOTH)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])

sphere = gluNewQuadric()

glMatrixMode(GL_PROJECTION)
gluPerspective(100, (display[0] / display[1]), 0.1, 100.0)
glMatrixMode(GL_MODELVIEW)

camera_x, camera_y, camera_z = 2.0, 3.0, 0.0
yaw = 0.0
pitch = -90.0 
camera_vel_z = 0.0
gravity = -0.02
jump_force = 0.20
on_ground = False

displayCenter = [display[0] // 2, display[1] // 2]
pygame.mouse.set_visible(False)
pygame.mouse.set_pos(displayCenter)

run = True
paused = False

height = 15
length = 15
maze_list = []

maze_list.append([
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
[1,0,1,0,1,0,1,1,0,1,0,1,1,0,1],
[1,0,1,0,0,0,1,0,0,0,0,1,0,0,1],
[1,0,1,1,1,0,1,0,1,1,0,1,1,0,1],
[1,0,1,0,0,0,0,0,1,0,0,1,0,0,1],
[1,0,1,0,1,1,1,0,1,1,1,1,1,0,1],
[1,0,0,0,1,0,0,0,0,1,0,0,1,0,1],
[1,1,1,0,1,0,1,1,0,1,1,0,1,0,1],
[1,0,0,0,0,0,1,0,0,0,1,0,1,0,1],
[1,0,1,1,1,1,1,0,1,0,1,0,1,0,1],
[1,0,0,0,0,0,0,0,1,0,0,0,1,0,0],
[1,1,1,1,1,1,1,0,1,1,1,0,1,1,1],
[1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
])
maze_list.append([
[1,1,1,1,1,1,1,1,1,1,1,0,1,1,1],
[1,0,0,0,1,0,0,1,0,1,0,0,1,0,1],
[1,0,1,0,1,1,0,1,0,1,0,1,1,0,1],
[1,0,1,0,0,0,0,0,0,1,0,0,1,0,1],
[1,0,1,1,1,1,1,1,0,1,1,0,1,0,1],
[1,0,0,0,0,0,0,1,0,0,1,0,0,0,1],
[1,1,1,1,1,0,1,1,1,1,1,1,1,0,1],
[1,0,0,0,1,0,0,0,0,1,0,0,1,0,1],
[1,0,1,0,1,1,1,1,0,1,1,0,1,0,1],
[1,0,1,0,0,0,0,0,0,0,1,0,1,0,1],
[1,0,1,1,1,1,1,1,1,0,1,0,0,0,1],
[1,0,0,0,0,0,0,0,1,0,0,0,1,0,1],
[1,1,1,0,1,1,1,1,1,1,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
])
maze_list.append([
[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
[1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
[1,0,1,0,1,0,1,1,1,0,1,0,1,0,1],
[1,0,1,0,0,0,0,0,1,0,0,0,1,0,1],
[1,0,1,1,1,1,1,0,1,1,1,0,1,0,1],
[1,0,0,0,0,0,1,0,0,0,1,0,0,0,1],
[1,1,1,1,1,0,1,0,1,0,1,1,1,0,1],
[1,0,0,0,0,0,0,0,0,1,0,0,1,0,1],
[1,0,1,0,1,1,1,1,0,1,1,0,1,0,1],
[1,0,1,0,0,0,0,0,0,0,1,0,1,0,1],
[1,0,1,1,1,1,1,1,1,0,1,0,1,0,1],
[1,0,0,0,0,0,0,0,1,0,0,0,1,0,1],
[1,0,1,1,1,1,1,1,1,1,1,1,1,0,1],
[1,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
[1,1,1,1,1,1,0,1,1,1,1,1,1,1,1]
])

maze = random.choice(maze_list)

def load_maze(maze):
    cube_bboxes = []
    height = len(maze)
    length = len(maze[0])

    for y in range(height):
        for x in range(length):
            if maze[y][x] == 1:
                cube_bboxes.append(create_cube_bbox(x, y, 0))
            elif maze[y][x] == 0:
                cube_bboxes.append(create_cube_bbox(x, y, -1))
                cube_bboxes.append(create_cube_bbox(x, y, 1))
                    
    return cube_bboxes

cube_bboxes = load_maze(maze)

camera_size = 0.5

def check_collision(x, y, z):
    cam_bbox = BoundingBox(
        x - camera_size, x + camera_size,
        y - camera_size, y + camera_size,
        z - camera_size, z + camera_size
    )
    
    for bbox in cube_bboxes:
        if cam_bbox.intersects(bbox):
            return True
    return False

def check_ground(x, y, z):
    test_bbox = BoundingBox(
        x - camera_size, x + camera_size,
        y - camera_size, y + camera_size,
        z - camera_size - 0.05, z + camera_size
    )

    for bbox in cube_bboxes:
        if test_bbox.intersects(bbox):
            return True
    # Check floor
    if z - camera_size <= -2:
        return True
    
    return False

def find_exit(maze):
    h = len(maze)
    w = len(maze[0])

    # Top row
    for x in range(w):
        if maze[0][x] == 0:
            return (x, 0)

    # Bottom row
    for x in range(w):
        if maze[h-1][x] == 0:
            return (x, h-1)

    # Left column
    for y in range(h):
        if maze[y][0] == 0:
            return (0, y)

    # Right column
    for y in range(h):
        if maze[y][w-1] == 0:
            return (w-1, y)

    return None

slow_traps = []
fast_traps = []
teleport_traps = []
reveal_traps = []

def placethings(maze, arrayname, count=3, duration=3):
    exit_pos = find_exit(maze)

    empty_cells = [
        (x, y)
        for y in range(len(maze))
        for x in range(len(maze[0]))
        if maze[y][x] == 0 and (x, y) != exit_pos
    ]

    random.shuffle(empty_cells)
    traps_to_place = min(count, len(empty_cells))

    for i in range(traps_to_place):
        x, y = empty_cells[i]

        # Mark trap in maze
        maze[y][x] = 2

        arrayname.append({
            'x': x,
            'y': y,
            'active': True,
            'duration': duration,
            'trigger_time': None
        })

def get_random_empty_cell(maze):
    empty_cells = [
        (x, y)
        for y in range(len(maze))
        for x in range(len(maze[0]))
        if maze[y][x] == 0  # only empty cells
    ]
    if not empty_cells:
        return None
    return random.choice(empty_cells)

placethings(maze,slow_traps, count=3,duration=3)
placethings(maze,fast_traps, count=2,duration=2)
placethings(maze, teleport_traps, count=1)
placethings(maze, reveal_traps, count=1, duration=6) 

def grid_to_world(x, y):
    # same scaling as verts()
    world_x = 2 * x
    world_y = 2 * y
    return world_x, world_y

def Checking(array, player_x, player_y):
    for trap in array[:]:  # iterate over a copy
        tx, ty = grid_to_world(trap['x'], trap['y'])
        if abs(player_x - tx) < 1 and abs(player_y - ty) < 1:
            duration = trap.get('duration', 0)
            array.remove(trap)  # delete trap after activation
            return duration
    return 0

def draw_trap(trap,tex,wee):
    # The trap is in maze grid coordinates (trap['x'], trap['y'])
    # Convert to same world coordinates as verts()
    vx = trap['x']
    vy = trap['y']
    vz = -.99  # same as maze cube
    CubeFloor(vx, vy, vz,tex,wee)
    
    
def reset_traps(maze, traps_array):
    # Reset maze cells where traps were placed (turn 2 → 0)
    for trap in traps_array:
        maze[trap['y']][trap['x']] = 0

    # Clear old traps
    traps_array.clear()
    
def loadTexture(path):
    textureSurface = pygame.image.load(path)
    textureData = pygame.image.tostring(textureSurface, "RGBA", True)
    width = textureSurface.get_width()
    height = textureSurface.get_height()

    texID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texID)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texID

def check_teleport(array, player_x, player_y):
    for trap in array[:]:  # iterate over a copy
        tx, ty = grid_to_world(trap['x'], trap['y'])
        if abs(player_x - tx) < 1 and abs(player_y - ty) < 1:
            array.remove(trap)  # delete teleport trap after use
            return True
    return False

slow_end_time = 0
fasttime=0
reveal_end_time = 0

wall_texture = loadTexture(r"/Users/andrew/COSC4370/peerreivew2/exit.jpg")
Floor = loadTexture(r"/Users/andrew/COSC4370/peerreivew2/floor.webp")
leave = loadTexture(r"/Users/andrew/COSC4370/peerreivew2/exit.jpg")
slow = loadTexture(r"/Users/andrew/COSC4370/peerreivew2/slow.jpg")
fast = loadTexture(r"/Users/andrew/COSC4370/peerreivew2/fast.png")
tel = loadTexture(r"/Users/andrew/COSC4370/peerreivew2/tel.jpg")
see = loadTexture(r"/Users/andrew/COSC4370/peerreivew2/see.jpg")
glEnable(GL_TEXTURE_2D)
glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

print("start")
while run:
    mouseMove = [0, 0]
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_RETURN:
                run = False
            if event.key == K_PAUSE or event.key == K_p:
                paused = not paused
                pygame.mouse.set_pos(displayCenter)
            if event.key == K_r:
                camera_x, camera_y, camera_z = 2.0, 3.0, 0.0
                yaw = 0.0
                pitch = -90.0 
                # Reset traps
                reset_traps(maze, slow_traps)
                reset_traps(maze, fast_traps)
                reset_traps(maze, teleport_traps)
                reset_traps(maze, reveal_traps)
                # Re-place traps
                placethings(maze,slow_traps, count=3,duration=3)
                placethings(maze,fast_traps, count=2,duration=2)
                placethings(maze, teleport_traps, count=1)
                placethings(maze, reveal_traps, count=1, duration=6) 
            if event.key == K_n:
                camera_x, camera_y, camera_z = 2.0, 3.0, 0.0
                yaw = 0.0
                pitch = -90.0 
                
                # Reset traps
                reset_traps(maze, slow_traps)
                reset_traps(maze, fast_traps)
                reset_traps(maze, teleport_traps)
                reset_traps(maze, reveal_traps)
                
                maze = random.choice(maze_list)
                cube_bboxes.clear()
                cube_bboxes = load_maze(maze)    
                
                # Re-place traps
                placethings(maze,slow_traps, count=3,duration=3)
                placethings(maze,fast_traps, count=2,duration=2)
                placethings(maze, teleport_traps, count=1)
                placethings(maze, reveal_traps, count=1, duration=6) 
        if event.type == MOUSEMOTION:
            mouseMove = [event.pos[i] - displayCenter[i] for i in range(2)]
        pygame.mouse.set_pos(displayCenter)

    print("step 1")
    yaw += mouseMove[0] * 0.1
    pitch += mouseMove[1] * 0.1
    pitch = max(-179, min(0, pitch))

    keys = pygame.key.get_pressed()
    speed = 0.15
    wee = speed
    
    duration = Checking(slow_traps, camera_x, camera_y)
    if duration > 0:
        slow_end_time = time.time() + duration
    
    duration = Checking(fast_traps, camera_x, camera_y)
    if duration > 0:
        fasttime = time.time() + duration
    
    if time.time() < slow_end_time:
        wee *= 0.4
    
    if time.time() < fasttime:
        wee *= 1.25

    old_x, old_y, old_z = camera_x, camera_y, camera_z
    camera_vel_z += gravity
    camera_z += camera_vel_z

    fx = -math.sin(math.radians(yaw)) * wee
    fy = -math.cos(math.radians(yaw)) * wee
    if keys[K_w]:
        camera_x -= fx
        camera_y -= fy  
    if keys[K_s]:
        camera_x += fx
        camera_y += fy

    sx = -math.sin(math.radians(yaw + 90)) * wee
    sy = -math.cos(math.radians(yaw + 90)) * wee
    
    if keys[K_d]:
        camera_x -= sx
        camera_y -= sy
    if keys[K_a]:
        camera_x += sx
        camera_y += sy
        
    if keys[K_SPACE] and on_ground:
        camera_vel_z = jump_force
        on_ground = False
        
    sphere_x = camera_x
    sphere_y = camera_y
    sphere_z = camera_z - 1.0

    if check_collision(camera_x, camera_y, camera_z):
        camera_x, camera_y = old_x, old_y
    
    if camera_vel_z < 0:  # only check downwards
        if check_ground(camera_x, camera_y, camera_z):
            on_ground = True
            camera_vel_z = 0
            while check_ground(camera_x, camera_y, camera_z - 0.01):
                camera_z += 0.01
        else:
            on_ground = False
    else:
        on_ground = False
        
    if check_teleport(teleport_traps, camera_x, camera_y):
        cell = get_random_empty_cell(maze)
        if cell:
            x, y = cell
            camera_x, camera_y = 2*x, 2*y  # convert grid to world coordinates
            camera_z = 0.2  # a little above the floor

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glRotatef(pitch, 1.0, 0.0, 0.0)
    glRotatef(yaw, 0.0, 0.0, 1.0)
    glTranslatef(-camera_x, -camera_y, -camera_z)
    
    duration = Checking(reveal_traps, camera_x, camera_y)
    if duration > 0:
        reveal_end_time = time.time() + duration

    exit_pos = find_exit(maze)
    glPushMatrix()
    for y in range(height):
        for x in range(length):
            if maze[y][x] == 1:
                if time.time() >= reveal_end_time:
                    Cube(x, y, 0, texture_coords, wall_texture)
            else:
                if (x, y) == find_exit(maze):
                    Cube(x, y, 0, texture_coords, leave)
                CubeFloor(x, y, -1, texture_coords, Floor)
                if time.time() >= reveal_end_time:
                    Cuberoof(x, y, 1, texture_coords, wall_texture)
    glPopMatrix()
    
    glLightfv(GL_LIGHT0, GL_POSITION, [camera_x, camera_y, camera_z, 1.0])
    
    for trap in slow_traps:
            draw_trap(trap,texture_coords, slow)
            
    for trap in fast_traps:
            draw_trap(trap,texture_coords, fast)
            
    for trap in teleport_traps:
            draw_trap(trap, texture_coords, tel)
            
    for trap in reveal_traps:
            draw_trap(trap, texture_coords, see)
            
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
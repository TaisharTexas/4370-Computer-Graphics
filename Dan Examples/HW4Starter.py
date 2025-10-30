import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math


vertices = ((1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
            (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1))


edges = ((0,1), (0,3), (0,4), (2,1), (2,3), (2,7), (6,3), (6,4),
         (6,7), (5,1), (5,4), (5,7))

texture_coords = [((0, 0), (1/3, 0), (1/3, 1/2), (0, 1/2)),
                  ((0, 1/2), (1/3, 1/2), (1/3, 1), (0, 1)),
                  ((1/3, 0), (2/3, 0), (2/3, 1/2), (1/3, 1/2)),
                  ((1/3, 1/2), (2/3, 1/2), (2/3, 1), (1/3, 1)),
                  ((2/3, 0), (1, 0), (1, 1/2), (2/3, 1/2)),
                  ((2/3, 1/2), (1, 1/2), (1, 1), (2/3, 1))]


surfaces = ((0,1,2,3), (3,2,7,6), (6,7,5,4), (4,5,1,0), (1,5,7,2), (4,0,3,6))


forced = False
def Cube(vx,vy,vz,texture):
    glBegin(GL_QUADS)

    for surface_index,surface in enumerate(surfaces):
        for vertex_index,vertex in enumerate(surface):
            glTexCoord2fv(texture[surface_index][vertex_index])
            glVertex3fv(vertices[vertex])
    glEnd()
    
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()


def loadTexture():
    textureSurface = pygame.image.load('../Data/cube_texture.png')
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
    width = textureSurface.get_width()
    height = textureSurface.get_height()

    glEnable(GL_TEXTURE_2D)
    texid = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    return texid


pygame.init()
display = (800, 800)
scree = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)


glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glShadeModel(GL_SMOOTH)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])


glMatrixMode(GL_PROJECTION)
gluPerspective(80, (display[0]/display[1]), 0.1, 50.0)

glMatrixMode(GL_MODELVIEW)
gluLookAt(0, -3, 0, 0, 0, 0, 0, 0, 1)
viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
glLoadIdentity()

loadTexture() # we aren't capturing the id, should we?

run = True
angle = 0 # Rotation angle about the vertical axis
glColor(1,1,1,1)

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN: # Capture an escape key press to exit
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                run = False

    # init model view matrix
    glLoadIdentity()

    # apply view matrix
    glMultMatrixf(viewMatrix)

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    glColor(1,1,1,1)
    tilt = 15 + 10 * math.cos(angle * math.pi/180) # Tilt as we rotate
    glRotate(tilt, 1, 0, 0) # Tilt a bit to be easier to see
    angle = (angle + 1) % 360
    glRotatef(angle, 0, 0, 1) # Rotate around the box's vertical axis
    Cube(0,0,0,texture_coords)

    # Draw the ground quad
    glColor4f(0.5, 0.5, 0.5, 1)
    glBegin(GL_QUADS)
    glVertex3f(-10, -10, -2)
    glVertex3f(10, -10, -2)
    glVertex3f(10, 10, -2)
    glVertex3f(-10, 10, -2)
    glEnd()

    glPopMatrix()

    pygame.display.flip()
    pygame.time.wait(30)

pygame.quit()
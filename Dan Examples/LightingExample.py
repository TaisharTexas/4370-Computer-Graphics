# -*- coding: utf-8 -*-
"""
This is a simple lighting example with a cube lit from below. 
The vertices are given different colors to show the interpolation across the 
faces. 
"""

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

VERTICES = (
    ( 1, -1, -1), # 0
    ( 1,  1, -1), # 1
    (-1,  1, -1), # 2
    (-1, -1, -1), # 3
    ( 1, -1,  1), # 4
    ( 1,  1,  1), # 5
    (-1, -1,  1), # 6
    (-1,  1,  1), # 7
    )

SURFACES = ((0,1,2,3), (3,2,7,6), (6,7,5,4), (4,5,1,0), (1,5,7,2), (4,0,3,6))

NORMALS = [
    ( 0,  0, -1),  # surface 0
    (-1,  0,  0),  # surface 1
    ( 0,  0,  1),  # surface 2
    ( 1,  0,  0),  # surface 3
    ( 0,  1,  0),  # surface 4
    ( 0, -1,  0)   # surface 5
]

COLORS = ((1,0,0), (0,0,1), (1,0,0), (0,0,1))

EDGES = ((0,1), (0,3), (0,4), (2,1), (2,3), (2,7), (6,3), (6,4), (6,7), (5,1), (5,4), (5,7))


def Cube():
    glBegin(GL_QUADS)
    for i_surface, surface in enumerate(SURFACES):
        glNormal3fv(NORMALS[i_surface])
        for i_vertex, vertex in enumerate(surface):
            index = (i_surface+i_vertex) % 2
            glColor3fv(COLORS[i_vertex])
            glVertex3fv(VERTICES[vertex])
    glEnd()

    glColor3fv((0,0,0))
    glBegin(GL_LINES)
    for edge in EDGES:
        for vertex in edge:
            glVertex3fv(VERTICES[vertex])
    glEnd()


def main():
    global SURFACES

    pygame.init()
    display = (800, 800)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    clock = pygame.time.Clock()

    glMatrixMode(GL_PROJECTION)
    gluPerspective(20, (display[0]/display[1]), 0.1, 50.0)

    glMatrixMode(GL_MODELVIEW)
    glTranslatef(0, 0, -15)

    glLight(GL_LIGHT0, GL_POSITION,  (0, -5.0, 0, 1)) # point light from the below
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))

    glEnable(GL_DEPTH_TEST) 
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()      

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)


        glRotatef(1, 3, 1, 1) # Slowly rotate the cube
        Cube()

        pygame.display.flip()
        clock.tick(50)

main()
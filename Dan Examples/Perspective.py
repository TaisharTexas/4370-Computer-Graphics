#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COSC 4370 Perspective code
This is a little code doodle to play wit the perspective view.
"""
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


def draw_axes():
    glLineWidth(5)
    glBegin(GL_LINES)
    glColor(1,0,0) # Red for the x-axis
    glVertex3fv((0,0,0))
    glVertex3fv((1.6,0,0))
    glColor(0,1,0) # Green for the y-axis
    glVertex3fv((0,0,0))
    glVertex3fv((0,1.6,0))
    glColor(0,0,1) # Blue for the z-axis
    glVertex3fv((0,0,0))
    glVertex3fv((0,0,1.6))
    glEnd()


def draw_cube():
    vertices = (
        (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
        (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
        )
    
    glBegin(GL_QUADS)

    # Front face
    glColor3f(1, 0, 0)  # Red
    glVertex3fv(vertices[6])
    glVertex3fv(vertices[4])
    glVertex3fv(vertices[5])
    glVertex3fv(vertices[7])

    # Back face
    glColor3f(0, 1, 0)  # Green
    glVertex3fv(vertices[3])
    glVertex3fv(vertices[2])
    glVertex3fv(vertices[1])
    glVertex3fv(vertices[0])

    # Top face
    glColor3f(0, 0, 1)  # Blue
    glVertex3fv(vertices[2])
    glVertex3fv(vertices[7])
    glVertex3fv(vertices[5])
    glVertex3fv(vertices[1])

    # Bottom face
    glColor3f(1, 1, 0)  # Yellow
    glVertex3fv(vertices[3])
    glVertex3fv(vertices[0])
    glVertex3fv(vertices[4])
    glVertex3fv(vertices[6])

    # Right face
    glColor3f(1, 0, 1)  # Magenta
    glVertex3fv(vertices[0])
    glVertex3fv(vertices[1])
    glVertex3fv(vertices[5])
    glVertex3fv(vertices[4])

    # Left face
    glColor3f(0, 1, 1)  # Cyan
    glVertex3fv(vertices[3])
    glVertex3fv(vertices[6])
    glVertex3fv(vertices[7])
    glVertex3fv(vertices[2])

    glEnd()



def main():
    pygame.init()
    display = (1000,1000)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('Persepctive Example')
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    #glOrtho(-20, 20, -20, 20, -20, 20)
    glMatrixMode(GL_PROJECTION)
    
    fovy = 40 # field of view (angle) in the y-direction
    gluPerspective(fovy, 1.0, 1.0, 20.0)
    glMatrixMode(GL_MODELVIEW)
    #gluLookAt(0, 0, 7, 0, 0, 0, 0, 1, 0)
    
    glTranslate(0,0,-7)
    glRotatef(30,1,0,0)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        keys = pygame.key.get_pressed() # Get pressed keys
        if keys[pygame.K_UP]:
            if(fovy < 150):
                fovy += 1
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(fovy, 1.0, 1.0, 20.0)

                glMatrixMode(GL_MODELVIEW)
                #gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)
                glLoadIdentity()
                glTranslate(0,0,-7)
                glRotatef(30,1,0,0)
                
        if keys[pygame.K_DOWN]:
            if(fovy > 30):
                fovy -= 1
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                gluPerspective(fovy, 1.0, 1.0, 20.0)
                glMatrixMode(GL_MODELVIEW)
                #gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)
                glLoadIdentity()
                glTranslate(0,0,-7)
                glRotatef(30,1,0,0)
        
        glRotatef(1, 0, math.cos(math.pi/6), -math.sin(math.pi/6))
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_axes() # Draw the axes
        draw_cube() # Draw the cube
        
        pygame.display.flip()
        pygame.time.wait(10)


main()
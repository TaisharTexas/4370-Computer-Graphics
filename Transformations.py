#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COSC 4370 
This file provides a simple way to try out different orders of transfprmations.
"""
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


def Axes():
    glBegin(GL_LINES)
    glColor(1,0,0) # Red for the x-axis
    glVertex3fv((0,0,0))
    glVertex3fv((1.5,0,0))
    glColor(0,1,0) # Green for the y-axis
    glVertex3fv((0,0,0))
    glVertex3fv((0,1.5,0))
    glColor(0,0,1) # Blue for the z-axis
    glVertex3fv((0,0,0))
    glVertex3fv((0,0,1.5))
    glEnd()


def Triangle(side = 1.0):
    glPushMatrix()
    glBegin(GL_TRIANGLES)
    
    glVertex3fv((-side/2, 0, 0))
    glVertex3fv((side/2, 0, 0))
    glVertex3fv((0, math.sqrt(3)/2, 0))
    
    glEnd()
    Axes()
    glPopMatrix()


pygame.init()
display = (1080,1080)
pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
pygame.display.set_caption('Transformation Examples')
glOrtho(-10, 10, -10, 10, -10, 10)
glMatrixMode(GL_MODELVIEW)

run = True
theta=0
angle=0

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False;
            break

    keys = pygame.key.get_pressed() # Get pressed keys

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)


    # NEW in class
    glPushMatrix()
    glColor(1.0,0,0)
    Triangle()

    glPushMatrix()
    glRotate(theta/2,0,0,1)
    theta+=0.2
    glTranslated(2.5,0,0)

    glColor(0,1.0,0)
    Triangle()
    glRotate(angle, 0, 0, 1)
    glTranslated(1.5, 0, 0)
    glRotate(angle*3, 0, 0, 1)
    angle+=1

    glColor(0,0,1)
    Triangle()

    glPopMatrix()
    glPopMatrix()


    # #ORIG
    # # Draw a red triangle
    # glColor(1.0, 0, 0) #set color
    # Triangle() #draw
    # glPushMatrix() #save as is
    # glRotate(45, 0, 0, 1) #rotate (b/c of the push, rotates a copy of sorts)
    # glScalef(2,2,2) #scale up
    # glTranslated(5, 0, 0) #translate
    # # Rotate, scale, and then translate and draw a green triangle
    # glColor(0, 1.0, 0) # set color
    # Triangle() #draw
    # glPopMatrix() #save as is
    # glPushMatrix()
    # glTranslated(5, 0, 0)
    # glRotate(45, 0, 0, 1)
    # # Translate then rotate and draw a blue triangle
    # glColor(0, 0, 1.0)
    # Triangle()
    # glPopMatrix()
    # glPopMatrix()
    
    pygame.display.flip()
    pygame.time.wait(10)


print('Done!')
pygame.quit()
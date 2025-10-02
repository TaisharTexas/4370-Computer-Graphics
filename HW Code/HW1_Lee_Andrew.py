#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COSC 4370 Homework #1
Andrew Lee's Submission for HW1

The images/gifs of the shapes on canvas still dont work for me but I did all the shapes listed
"""

import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


def Cube():
    d = math.sqrt(1/3)
    verticies = (
        (d, -d, -d),
        (d, d, -d),
        (-d, d, -d),
        (-d, -d, -d),
        (d, -d, d),
        (d, d, d),
        (-d, -d, d),
        (-d, d, d)
        )

    edges = (
        (0,1), (0,3), (0,4), (2,1), (2,3), (2,7),
        (6,3), (6,4), (6,7), (5,1), (5,4), (5,7)
        )
    glColor(1,1,1) # Draw the cube in white
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()

def Tetrahedron():
    d = math.sqrt(1 / 3)
    verticies = (
        (d, d, -d),
        (-d, -d, -d),
        (d, -d, d),
        (-d, d, d)
    )

    edges = (
        (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)
    )
    glColor(1, 1, 1)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()

def Octehedron():
    d = 1
    verticies = (
        (d, 0, 0),
        (-d, 0, 0),
        (0, d, 0),
        (0, -d, 0),
        (0, 0, d),
        (0, 0, -d)
    )
    edges = (
        (0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)
    )

    glColor3f(1, 1, 1)  # White lines
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()

#ToDo: NOTE TO GRADER: this shape is where my brain exploded and I just looked up how on earth to even think about this and
# I got the list of verticies and edges and stuff. WHY THESE SHAPES SO COMPLICATED
def Dodecahedron():
    phi = (1 + math.sqrt(5)) / 2
    d = 1 / math.sqrt(3)
    verticies = (
        # Cube vertices
        (d, d, d),
        (d, d, -d),
        (d, -d, d),
        (d, -d, -d),
        (-d, d, d),
        (-d, d, -d),
        (-d, -d, d),
        (-d, -d, -d),

        # Golden rectangle vertices in xy plane
        (0, d / phi, d * phi),
        (0, d / phi, -d * phi),
        (0, -d / phi, d * phi),
        (0, -d / phi, -d * phi),

        # Golden rectangle vertices in xz plane
        (d / phi, d * phi, 0),
        (d / phi, -d * phi, 0),
        (-d / phi, d * phi, 0),
        (-d / phi, -d * phi, 0),

        # Golden rectangle vertices in yz plane
        (d * phi, 0, d / phi),
        (d * phi, 0, -d / phi),
        (-d * phi, 0, d / phi),
        (-d * phi, 0, -d / phi)
    )

    edges = (
        # Face 1: vertices 0, 16, 2, 10, 8
        (0, 16), (16, 2), (2, 10), (10, 8), (8, 0),
        # Face 2: vertices 0, 8, 4, 14, 12
        (0, 8), (8, 4), (4, 14), (14, 12), (12, 0),
        # Face 3: vertices 0, 12, 1, 17, 16
        (0, 12), (12, 1), (1, 17), (17, 16), (16, 0),
        # Face 4: vertices 1, 9, 11, 3, 17
        (1, 9), (9, 11), (11, 3), (3, 17), (17, 1),
        # Face 5: vertices 1, 12, 14, 5, 9
        (1, 12), (12, 14), (14, 5), (5, 9), (9, 1),
        # Face 6: vertices 2, 16, 17, 3, 13
        (2, 16), (16, 17), (17, 3), (3, 13), (13, 2),
        # Face 7: vertices 2, 13, 15, 6, 10
        (2, 13), (13, 15), (15, 6), (6, 10), (10, 2),
        # Face 8: vertices 3, 11, 7, 15, 13
        (3, 11), (11, 7), (7, 15), (15, 13), (13, 3),
        # Face 9: vertices 4, 8, 10, 6, 18
        (4, 8), (8, 10), (10, 6), (6, 18), (18, 4),
        # Face 10: vertices 4, 18, 19, 5, 14
        (4, 18), (18, 19), (19, 5), (5, 14), (14, 4),
        # Face 11: vertices 5, 19, 7, 11, 9
        (5, 19), (19, 7), (7, 11), (11, 9), (9, 5),
        # Face 12: vertices 6, 15, 7, 19, 18
        (6, 15), (15, 7), (7, 19), (19, 18), (18, 6)
    )
    #Theres some duplicate edges in that list and im not sure that it actually matters but I filtered them down to just uniques
    # (im sure with bigger shapes the reduction in duplicated helps with performance?)
    unique_edges = []
    edge_set = set()
    for edge in edges:
        sorted_edge = tuple(edge)
        if sorted_edge not in edge_set:
            edge_set.add(sorted_edge)
            unique_edges.append(edge)

    glColor(1, 1, 1)
    glBegin(GL_LINES)
    for edge in unique_edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()

#ToDo: NOTE TO GRADER: looked up this one too lol my brain too small to do this in my head
def Icosahedron():
    phi = (1 + math.sqrt(5)) / 2
    d = 1 / math.sqrt(3)
    verticies = (
        (0, d, d * phi),  # 0
        (0, d, -d * phi),  # 1
        (0, -d, d * phi),  # 2
        (0, -d, -d * phi),  # 3

        (d, d * phi, 0),  # 4
        (d, -d * phi, 0),  # 5
        (-d, d * phi, 0),  # 6
        (-d, -d * phi, 0),  # 7

        (d * phi, 0, d),  # 8
        (d * phi, 0, -d),  # 9
        (-d * phi, 0, d),  # 10
        (-d * phi, 0, -d)  # 11
    )
    edges = (
        # Top cap (5 triangular faces around vertex 0)
        (0, 2), (2, 8), (8, 0),  # Triangle 1: 0-2-8
        (0, 8), (8, 4), (4, 0),  # Triangle 2: 0-8-4
        (0, 4), (4, 6), (6, 0),  # Triangle 3: 0-4-6
        (0, 6), (6, 10), (10, 0),  # Triangle 4: 0-6-10
        (0, 10), (10, 2), (2, 0),  # Triangle 5: 0-10-2

        # Upper belt (5 triangular faces)
        (2, 10), (10, 7), (7, 2),  # Triangle 6: 2-10-7
        (2, 7), (7, 5), (5, 2),  # Triangle 7: 2-7-5
        (2, 5), (5, 8), (8, 2),  # Triangle 8: 2-5-8
        (8, 5), (5, 9), (9, 8),  # Triangle 9: 8-5-9
        (8, 9), (9, 4), (4, 8),  # Triangle 10: 8-9-4

        # Lower belt (5 triangular faces)
        (4, 9), (9, 1), (1, 4),  # Triangle 11: 4-9-1
        (4, 1), (1, 6), (6, 4),  # Triangle 12: 4-1-6
        (6, 1), (1, 11), (11, 6),  # Triangle 13: 6-1-11
        (6, 11), (11, 10), (10, 6),  # Triangle 14: 6-11-10
        (10, 11), (11, 7), (7, 10),  # Triangle 15: 10-11-7

        # Bottom cap (5 triangular faces around vertex 3)
        (7, 11), (11, 3), (3, 7),  # Triangle 16: 7-11-3
        (7, 3), (3, 5), (5, 7),  # Triangle 17: 7-3-5
        (5, 3), (3, 9), (9, 5),  # Triangle 18: 5-3-9
        (9, 3), (3, 1), (1, 9),  # Triangle 19: 9-3-1
        (1, 3), (3, 11), (11, 1)  # Triangle 20: 1-3-11
    )
    #same thing about unique edges here
    unique_edges = []
    edge_set = set()
    for edge in edges:
        sorted_edge = tuple(edge)
        if sorted_edge not in edge_set:
            edge_set.add(sorted_edge)
            unique_edges.append(edge)

    glColor(1, 1, 1)
    glBegin(GL_LINES)
    for edge in unique_edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()


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


def Circle():
    glPushMatrix()
    glLoadIdentity()
    glOrtho(-2, 2, -2, 2, -2, 2)
    glColor(1,0,1) # Purple for the limits
    glBegin(GL_LINE_LOOP)
    for i in range(36):
        angle = 2.0 * math.pi * i / 36
        x = math.cos(angle)
        y = math.sin(angle)
        glVertex3fv((x, y, 0))
    glEnd()
    glPopMatrix()
    

def main():
    pygame.init()
    display = (800,800)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('Homework #1 - Submission by Andrew Lee')
    glOrtho(-2, 2, -2, 2, -2, 2)
    glMatrixMode(GL_MODELVIEW)

    keyPressed = -1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN:
                keyPressed = event.key
                print(event.key)



        glRotatef(1, 2, .9, .25)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        Axes()
        Circle()
        if(keyPressed == 49):    #1 key
            Cube()
        elif(keyPressed == 50):  #2 key
            Tetrahedron()
        elif (keyPressed == 51): #3 key
            Octehedron()
        elif (keyPressed == 52): #4 key
            Dodecahedron()
        elif (keyPressed == 53): #5 key
            Icosahedron()

        pygame.display.flip()
        pygame.time.wait(10)


main()
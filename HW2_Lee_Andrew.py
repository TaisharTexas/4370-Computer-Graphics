
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *

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

# need a sphere function
    # maybe with parameters for color, radius, and orbital rate
    # or an orbit function that applies translation to a sphere object




def main():
    pygame.init()
    display = (1080, 1080)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('Homework #2 - Submission by Andrew Lee')
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

        if keyPressed == 1073741905:
            print("down key pressed")
            keyPressed = -1 # reset key to neutral so it only does this rotation command once

        elif keyPressed == 1073741906:
            print("up key pressed")
            keyPressed = -1 # reset key to neutral so it only does this rotation command once


        glRotatef(1, 2, .9, .25)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        Circle()

        pygame.display.flip()
        pygame.time.wait(10)


main()
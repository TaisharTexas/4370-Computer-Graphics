"""
COSC 4370 Exam 10/20
Andrew Lee's Submission for Midterm

(5 pts) Draw a yellow sphere at the center of some size X, centered in the frame using Orthographic projection with a square window of size 5X on a side.
(10 pts.) Draw a red sphere of radius X/4 at a radius of 2X from the center orbiting around the center in a horizontal plane and moving quickly.
(10 pts.) Draw a green sphere of radius X/4 at a radius of 2X from the center orbiting around the center, tilted 60 degrees from the horizontal, and moving quickly.
(10 pts.) Draw a blue sphere of radius X/4 at a radius of 2X from the center orbiting around the center, tilted 60 degrees from the horizontal, and moving quickly.
(5 pts.) Enable the left and right arrow keys to rotate the entire model about the vertical axis +/- 45 degrees.
(5 pts.) Enable the up and down arrow keys to rotate the entire model about the horizontal axis +/- 45 degrees.
(5 pts.) Space the spheres so they do not collide at the crossing point and enable a reset of the rotations with the "r" key .

"""

import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from enum import Enum

# this is totally extra and why are python enums so weird but I wanted to just call the color names down in the main method
class Color(Enum):
    BLUE = [0, 0, 255]
    YELLOW = [255, 255, 0] #S1 - rX @ center
    GRAY = [128, 128, 128]
    LIGHT_GRAY = [211, 211, 211]
    GREEN = [0, 128, 0]
    RED = [255, 0, 0] #S2 -
    PURPLE = [148, 0, 211]

    def __getitem__(self, index):
        return self.value[index]
    def __iter__(self):
        return iter(self.value)

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


# use to draw orbit circles
def Circle(radius, color):
    glPushMatrix()
    glColor(color[0]/255.0, color[1]/255.0, color[2]/255.0)
    glBegin(GL_LINE_LOOP)
    for i in range(72):  # More segments for smoother circle
        angle = 2.0 * math.pi * i / 72
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        glVertex3fv((x, y, -0.1))  # Move orbit slightly behind
    glEnd()
    glPopMatrix()


# use to draw planets
def Sphere(radius, color):
    glColor(color[0]/255.0, color[1]/255.0, color[2]/255.0)

    # Create a quadric object
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)  # Solid fill

    gluSphere(quadric, radius, 40, 20)  # radius, slices, stacks
    gluDeleteQuadric(quadric)



def main():
    """ the MAIN size reference var"""
    sizeX = 200

    pygame.init()
    display = (sizeX*5, sizeX*5) #display will be 1k by 1k same as solar system one
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Solar System - Andrew Lee')

    # Set up perspective and enable depth testing
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-sizeX*2.5, sizeX*2.5, -sizeX*2.5, sizeX*2.5, -sizeX*2.5, sizeX*2.5)
    glMatrixMode(GL_MODELVIEW)

    # controls how much each object rotates each loop iteration
    thetaRed = 0
    thetaGreen = 120 # offsetting start pos so the balls dont hit
    thetaBlue = 90 # offsetting start pos so the balls dont hit


    redOrbitRate = 5.0  # (change this to increase or decrease speed of the entire model)
    greenOrbitRate = redOrbitRate  # (dont change)
    blueOrbitRate = redOrbitRate  # (dont change)


    viewAngleH = 90
    viewAngleV = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Handle key presses
        keys = pygame.key.get_pressed()


        #Enable the left and right arrow keys to rotate the entire model about the vertical axis +/- 45 degrees.
        if keys[pygame.K_DOWN]:
            #rotate up
            if viewAngleH <= 90 + 43:
                viewAngleH += 2
                print("viewAngleH:" + str(viewAngleH))
        if keys[pygame.K_UP]:
            #rotate down
            if viewAngleH >= 90-43:
                viewAngleH -= 2
                print("viewAngleH:" + str(viewAngleH))
        # Enable the up and down arrow keys to rotate the entire model about the horizontal axis +/- 45 degrees.
        if keys[pygame.K_LEFT]:
            # rotate left
            if viewAngleV <= 43:
                viewAngleV += 2
                print("viewAngleV:" + str(viewAngleV))
        if keys[pygame.K_RIGHT]:
            # rotate right
            if viewAngleV >= -43:
                viewAngleV -= 2
                print("viewAngleV:" + str(viewAngleV))


        # Space the spheres so they do not collide at the crossing point and enable a reset of the rotations with the "r" key .
        if keys[pygame.K_r]:
            # reset orbits
            print("reset orbit key pressed")
            thetaRed = 0
            thetaGreen = 120
            thetaBlue = 90

        # added for my own troubleshooting cause this thing disorients me so bad lol
        if keys[pygame.K_c]:
            print("reset camera key pressed")
            viewAngleH = 90
            viewAngleV = 0

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glRotate(viewAngleH, 1, 0, 0)
        glRotate(viewAngleV, 0, 0, 1)
        # Axes()

        glPushMatrix()
        Circle(sizeX*2, Color.RED) #red orbit
        glPopMatrix()

        glPushMatrix()
        glRotate(60, 0, 1, 0)
        Circle(sizeX*2, Color.GREEN) # green orbit
        glPopMatrix()

        glPushMatrix()
        glRotate(-60, 0, 1, 0)
        Circle(sizeX*2, Color.BLUE) #blue orbit
        glPopMatrix()

        # Draw a yellow sphere at the center of some size X, centered in the frame using Orthographic projection with a square window of size 5X on a side.
        glPushMatrix()
        Sphere(sizeX, Color.YELLOW)

        # Draw a red sphere of radius X/4 at a radius of 2X from the center orbiting around the center in a horizontal plane and moving quickly.
        glPushMatrix()
        Circle(sizeX * 2, Color.RED)  # red orbit
        glRotate(thetaRed, 0, 0, 1)
        thetaRed += redOrbitRate
        glTranslated(sizeX*2, 0, 0)
        Sphere(sizeX/4, Color.RED)
        glPopMatrix()  # pop red

        # Draw a green sphere of radius X/4 at a radius of 2X from the center orbiting around the center, tilted 60 degrees from the horizontal, and moving quickly.
        glPushMatrix()
        glRotate(60, 0,1,0)
        glRotate(thetaGreen, 0, 0, 1)
        thetaGreen += greenOrbitRate
        glTranslated(sizeX*2, 0, 0)
        Sphere(sizeX/4, Color.GREEN)
        glPopMatrix()  # pop green

        # Draw a blue sphere of radius X/4 at a radius of 2X from the center orbiting around the center, tilted 60 degrees from the horizontal, and moving quickly.
        glPushMatrix()
        glRotate(-60, 0, 1, 0)
        glRotate(thetaBlue, 0, 0, 1)
        thetaBlue += blueOrbitRate
        glTranslated(sizeX*2, 0, 0)
        Sphere(sizeX/4, Color.BLUE)
        glPopMatrix()  # pop blue


        glPopMatrix()  # pop yellow

        pygame.display.flip()
        pygame.time.wait(20)


if __name__ == "__main__":
    main()
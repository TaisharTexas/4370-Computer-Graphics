"""
COSC 4370 Homework #2
Andrew Lee's Submission for HW2

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
    YELLOW = [255, 255, 0]
    GRAY = [128, 128, 128]
    LIGHT_GRAY = [211, 211, 211]
    GREEN = [0, 128, 0]
    RED = [255, 0, 0]
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
def Circle(radius):
    glPushMatrix()
    glColor(0.3, 0.3, 0.3)  # Darker gray for orbit lines
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
    glColor(color[0], color[1], color[2])

    # Create a quadric object
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)  # Solid fill

    gluSphere(quadric, radius, 40, 20)  # radius, slices, stacks
    gluDeleteQuadric(quadric)



def main():
    pygame.init()
    display = (1000, 1000)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Solar System - Andrew Lee')

    # Set up perspective and enable depth testing
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-20, 20, -20, 20, -20, 20)
    glMatrixMode(GL_MODELVIEW)

    # controls how much each object rotates each loop iteration
    thetaEarth = 0
    thetaMars = 0
    thetaVenus = 0
    thetaMercury = 0
    thetaMoon = 0

    # earth orbit rate is 365.26 = 1.0
    earthOrbitRate = 1.0  # (change this to increase or decrease speed of the entire model)
    marsOrbitRate = earthOrbitRate * (365.26 / 686.98)  # (dont change)
    venusOrbitRate = earthOrbitRate * (365.26 / 224.70)  # (dont change)
    mercuryOrbitRate = earthOrbitRate * (365.26 / 87.97)  # (dont change)
    moonOrbitRate = earthOrbitRate * (365.26 / 27.3)  # (dont change)

    viewAngle = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Handle key presses
        keys = pygame.key.get_pressed()

        if keys[pygame.K_DOWN]:
            #rotate up
            if viewAngle >= 2:
                viewAngle -= 2
                print(viewAngle)
        if keys[pygame.K_UP]:
            #rotate down
            if viewAngle <= 88:
                viewAngle += 2
                print(viewAngle)
        if keys[pygame.K_LEFT]:
            #decrease speed of model
            if earthOrbitRate > 0.2:
                earthOrbitRate -= 0.1
                marsOrbitRate = earthOrbitRate * (365.26 / 686.98)  # (dont change)
                venusOrbitRate = earthOrbitRate * (365.26 / 224.70)  # (dont change)
                mercuryOrbitRate = earthOrbitRate * (365.26 / 87.97)  # (dont change)
                moonOrbitRate = earthOrbitRate * (365.26 / 27.3)  # (dont change)
                print(earthOrbitRate)
        if keys[pygame.K_RIGHT]:
            #increase speed of model
            if earthOrbitRate < 3.0:
                earthOrbitRate += 0.1
                marsOrbitRate = earthOrbitRate * (365.26 / 686.98)  # (dont change)
                venusOrbitRate = earthOrbitRate * (365.26 / 224.70)  # (dont change)
                mercuryOrbitRate = earthOrbitRate * (365.26 / 87.97)  # (dont change)
                moonOrbitRate = earthOrbitRate * (365.26 / 27.3)  # (dont change)
                print(earthOrbitRate)

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        glRotate(viewAngle, 1, 0, 0)
        # Axes()

        # Draw planet orbits (not the moon because that one needs to get moved as earth moves)
        Circle(10.0)
        Circle(3.9)
        Circle(7.2)
        Circle(15.0)

        # Sun (hisss...it burrnnnnssss)
        glPushMatrix()
        Sphere(2.0, Color.YELLOW)

        # Earth (its a bloody mess of a marble but its home)
        glPushMatrix()
        glRotate(thetaEarth, 0, 0, 1)
        thetaEarth += earthOrbitRate
        glTranslated(10.0, 0, 0)
        Sphere(1.0, Color.BLUE)

        # insert moon stuff here
        Circle(1.5)  # moon orbit circle

        glPushMatrix()
        glRotate(thetaMoon, 0, 0, 1)
        thetaMoon += moonOrbitRate
        glTranslated(1.5, 0, 0)
        Sphere(0.27, Color.GRAY)

        glPopMatrix()  # pop Moon
        glPopMatrix()  # pop Earth

        # Mars (the Tachi was legitimate salvage change my mind)
        glPushMatrix()
        glRotate(thetaMars, 0, 0, 1)
        thetaMars += marsOrbitRate
        glTranslated(15, 0, 0)
        Sphere(0.53, Color.RED)
        glPopMatrix()  # pop Mars

        # Venus (she's either a trap or true love...maybe both)
        glPushMatrix()
        glRotate(thetaVenus, 0, 0, 1)
        thetaVenus += venusOrbitRate
        glTranslated(7.2, 0, 0)
        Sphere(0.95, Color.PURPLE)
        glPopMatrix()  # pop venus

        # Mercury (a whole planet sized barometer...huh)
        glPushMatrix()
        glRotate(thetaMercury, 0, 0, 1)
        thetaMercury += mercuryOrbitRate
        glTranslated(3.9, 0, 0)
        Sphere(0.38, Color.GREEN)
        glPopMatrix()  # pop mercury

        glPopMatrix()  # pop's sun

        pygame.display.flip()
        pygame.time.wait(20)


if __name__ == "__main__":
    main()
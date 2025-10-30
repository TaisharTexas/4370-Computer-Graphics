"""
Overview:
- Building on our work from the first two assignments, we would like to be able to texture objects using triangles and/or
quads. To demonstrate these ideas, we will be drawing on the concepts of constructing shapes from the first assignment
and the surfaces and transforms from the second. We will create a set of textured polyhedrons in the form of dice.
We will place number textures so that each face receives a different number.

Specifications:
- Starting with the code from previous assignments, generate the 4-, 6-, 8-, 12-, and 20-sided textured figures using
triangles or quads as appropriate. You are given as and example, a cube (companion cube) with the same texture applied
to each face. Modify it to be a 6-sided dice by adding a unique number from 1-6 to each face of the cube to practice the
concepts needed for the more complex problem. Then, proceed to the main problem of constructing the remaining solids
with dice faces.

- You may construct these regular polyhedrons in an color you wish. Create and modify the texture and texture mapping so
that each face has a unique value. Use the existing perspective camera and rotational motion to show off the faces of
your dodecahedron. Ensure that you can switch between the shapes with a number press.

Deliverables:
- Submit a single python file and any texture files of any appropriate type to Canvas, including the required specifications.
- The program should display the colored platonic solids,  Tetrahedron, Cube, Octahedron, Dodecahedron and Icosahedron.
- Provide a mechanism to change the shape displayed with a numerical keypress (1-5).
- Each face on each shape should hold a different number, with opposite faces summing up to n+1, where n is the number of
sides on the polyhedron.
- You may use any color for the faces. Selecting a contrasting color for the numbers to improve visibility.
- You may position the numbers in any orientation and use any arrangement of numbers on the faces that you wish as long
as you include all the numbers for each polyhedron.

Notes:
- Be sure to select a reasonable size for your object (the values you found for vertices should work well.
- Use the code you developed for the first Homework and the starter code to complete this problem.
- Be sure to sure to start this program early as there are many small details.
- There are many free options for image editor to select.
"""

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math

"""
just fyi, I used AI to generate the dice texture images 
"""
def loadTextures():

    textures = []
    for i in range(1,21):
        textureSurface = pygame.image.load(f'../Data/{i}.png')
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
        textures.append(texid)

    return textures

# take your d4 guidance
def d4(textures):
    d = math.sqrt(1 / 3)
    vertices = (
        (d, d, -d),
        (-d, -d, -d),
        (d, -d, d),
        (-d, d, d)
    )
    edges = (
        (0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)
    )
    surfaces = (
        (0, 2, 1), (0, 3, 2), (0, 1, 3), (1, 2, 3)
    )

    face_numbers = [1, 4, 2, 3]

    # had to play a lot with these nums to get the positioning and zoom right (will re-use for all triangle face shapes)
    #                   X               Y           Z
    texture_coords = ((0.5, -0.25), (-0.25, 0.7), (1.25, 1.25))

    # surfaces w/ nums
    for surface_index, surface in enumerate(surfaces):
        numOnFace = face_numbers[surface_index]
        glBindTexture(GL_TEXTURE_2D, textures[numOnFace - 1])

        glBegin(GL_TRIANGLES)
        for vertex_index, vertex in enumerate(surface):
            glTexCoord2fv(texture_coords[vertex_index])
            glVertex3fv(vertices[vertex])
        glEnd()

    # black edges
    glDisable(GL_TEXTURE_2D)
    glColor4f(0, 0, 0, 1)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)

# I didnt ask how small the room is we're in, I said, I. CAST. FIREBALL.
def d6(textures):
    d = math.sqrt(1 / 3)
    vertices = (
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
        (0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7),
        (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7)
    )
    surfaces = ((0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4), (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6))

    # texture_coords = [((0, 0), (1 / 3, 0), (1 / 3, 1 / 2), (0, 1 / 2)),
    #                   ((0, 1 / 2), (1 / 3, 1 / 2), (1 / 3, 1), (0, 1)),
    #                   ((1 / 3, 0), (2 / 3, 0), (2 / 3, 1 / 2), (1 / 3, 1 / 2)),
    #                   ((1 / 3, 1 / 2), (2 / 3, 1 / 2), (2 / 3, 1), (1 / 3, 1)),
    #                   ((2 / 3, 0), (1, 0), (1, 1 / 2), (2 / 3, 1 / 2)),
    #                   ((2 / 3, 1 / 2), (1, 1 / 2), (1, 1), (2 / 3, 1))]

    # not using the given coords from the example because I split all my textures into different files
    texture_coords = ((0, 0), (1, 0), (1, 1), (0, 1))

    face_numbers = [1, 6, 2, 5, 3, 4]


    # surfaces w/ nums
    for surface_index,surface in enumerate(surfaces):

        numOnFace = face_numbers[surface_index]
        glBindTexture(GL_TEXTURE_2D, textures[numOnFace - 1])

        glBegin(GL_QUADS)
        for vertex_index,vertex in enumerate(surface):
            glTexCoord2fv(texture_coords[vertex_index])
            glVertex3fv(vertices[vertex])
        glEnd()

    # black edges
    glDisable(GL_TEXTURE_2D)
    glColor4f(0, 0, 0, 1)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)

# bardic inspiration baby
def d8(textures):
    d = 1
    vertices = (
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
    surfaces = (
        (0, 2, 4),
        (0, 4, 3),
        (0, 3, 5),
        (0, 5, 2),
        (1, 4, 2),
        (1, 3, 4),
        (1, 5, 3),
        (1, 2, 5),
    )
    face_numbers = [1,7,5,3,4,6,8,2]
    texture_coords = ((0.5, -0.25), (-0.25, 0.7), (1.25, 1.25))

    # surfaces w/ nums
    for surface_index, surface in enumerate(surfaces):

        numOnFace = face_numbers[surface_index]
        glBindTexture(GL_TEXTURE_2D, textures[numOnFace - 1])

        glBegin(GL_TRIANGLES)
        for vertex_index, vertex in enumerate(surface):
            glTexCoord2fv(texture_coords[vertex_index])
            glVertex3fv(vertices[vertex])
        glEnd()

    # black edges
    glDisable(GL_TEXTURE_2D)
    glColor4f(0, 0, 0, 1)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)

# mwaahaa my great axe will smite you
def d12(textures):
    phi = (1 + math.sqrt(5)) / 2
    d = 1 / math.sqrt(3)
    vertices = (
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
    surfaces = (
        (0, 16, 2, 10, 8),
        (0, 8, 4, 14, 12),
        (0, 12, 1, 17, 16),
        (1, 9, 11, 3, 17),
        (1, 12, 14, 5, 9),
        (2, 16, 17, 3, 13),
        (2, 13, 15, 6, 10),
        (3, 11, 7, 15, 13),
        (4, 8, 10, 6, 18),
        (4, 18, 19, 5, 14),
        (5, 19, 7, 11, 9),
        (6, 15, 7, 19, 18)
    )
    face_numbers = [1,2,3,4,5,6,7,8,9,10,11,12] #yeah I gave but trying to follow the actual face order on my dice with this one lol

    # erm, ok so mine works...but its ugly...ai suggested the fancy math version that looks pretty, so im using that
    # texture_coords = ((0, 0), (1, 0), (1, 1), (0, 1), (0.5, 1))
    texture_coords = tuple(
        (0.5 + 0.7 * math.cos(2 * math.pi * i / 5),
         0.5 + 0.7 * math.sin(2 * math.pi * i / 5))
        for i in range(5)
    )

    # surfaces w/ nums
    for surface_index, surface in enumerate(surfaces):
        numOnFace = face_numbers[surface_index]
        glBindTexture(GL_TEXTURE_2D, textures[numOnFace - 1])

        glBegin(GL_POLYGON)  # For pentagons
        for vertex_index, vertex in enumerate(surface):
            glTexCoord2fv(texture_coords[vertex_index])  # You'll need 5 texture coords
            glVertex3fv(vertices[vertex])
        glEnd()

    # black edges
    unique_edges = []
    edge_set = set()
    for edge in edges:
        sorted_edge = tuple(edge)
        if sorted_edge not in edge_set:
            edge_set.add(sorted_edge)
            unique_edges.append(edge)

    glDisable(GL_TEXTURE_2D)
    glColor4f(0, 0, 0, 1)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)

# ROLL FOR INITIATIVE
def d20(textures):
    phi = (1 + math.sqrt(5)) / 2
    d = 1 / math.sqrt(3)
    vertices = (
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
    surfaces = (
        (0,2,8),
        (0,4,8),
        (0,4,6),
        (0,6,10),
        (0,2,10),
        (2,10,7),
        (2,5,7),
        (2,5,8),
        (5,8,9),
        (4,8,9),
        (1,4,9),
        (1,4,6),
        (1,6,11),
        (6,11,10),
        (7,10,11),
        (3,7,11),
        (3,5,7),
        (3,5,9),
        (1,3,9),
        (1,3,11)
    )
    face_numbers = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    texture_coords = ((0.5, -0.25), (-0.1, 0.7), (1.25, 1.25))
    # texture_coords = ((.4, -0.25), (-.2, .6), (1.2, 1.4))

    # surfaces w/ nums
    for surface_index, surface in enumerate(surfaces):
        numOnFace = face_numbers[surface_index]
        glBindTexture(GL_TEXTURE_2D, textures[numOnFace - 1])

        glBegin(GL_TRIANGLES)
        for vertex_index, vertex in enumerate(surface):
            glTexCoord2fv(texture_coords[vertex_index])
            glVertex3fv(vertices[vertex])
        glEnd()

    # black edges
    unique_edges = []
    edge_set = set()
    for edge in edges:
        sorted_edge = tuple(edge)
        if sorted_edge not in edge_set:
            edge_set.add(sorted_edge)
            unique_edges.append(edge)

    glDisable(GL_TEXTURE_2D)
    glColor4f(0, 0, 0, 1)
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

    glEnable(GL_TEXTURE_2D)
    # glColor3f(1, 1, 1)

def main():
    pygame.init()
    display = (800, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption('Homework #4 - Submission by Andrew Lee')

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

    textures = loadTextures()  # we aren't capturing the id, should we?

    run = True
    angle = 0  # Rotation angle about the vertical axis
    glColor(1, 1, 1, 1)

    keyPressed = 5
    viewAngleH = 0


    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:  # Capture an escape key press to exit
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    run = False
                elif event.key == pygame.K_1:
                    keyPressed = 1
                    print("Switched to d4")
                elif event.key == pygame.K_2:
                    keyPressed = 2
                    print("Switched to d6")
                elif event.key == pygame.K_3:
                    keyPressed = 3
                    print("Switched to d8")
                elif event.key == pygame.K_4:
                    keyPressed = 4
                    print("Switched to d12")
                elif event.key == pygame.K_5:
                    keyPressed = 5
                    print("Switched to d20")
                # elif event.key == pygame.K_DOWN:
                #     if viewAngleH < 45:
                #         viewAngleH += 2
                #         print("viewAngleH:" + str(viewAngleH))
                # elif event.key == pygame.K_UP:
                #     if viewAngleH > -45:
                #         viewAngleH -= 2
                #         print("viewAngleH:" + str(viewAngleH))

        # init model view matrix
        glLoadIdentity()
        glRotate(viewAngleH, 1, 1, 0)

        # apply view matrix
        glMultMatrixf(viewMatrix)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()
        glColor(1, 1, 1, 1)
        tilt = 15 + 10 * math.cos(angle * math.pi / 180)  # Tilt as we rotate
        glRotate(tilt, 1, 0, 0)  # Tilt a bit to be easier to see
        angle = (angle + 1) % 360
        glRotatef(angle, 0, 0, 1)  # Rotate around the box's vertical axis

        if keyPressed == 1:
            d4(textures)
        elif keyPressed == 2:
            d6(textures)
        elif keyPressed == 3:
            d8(textures)
        elif keyPressed == 4:
            d12(textures)
        elif keyPressed == 5:
            d20(textures)

        glPopMatrix()

        # Draw the ground quad
        glColor4f(0.65, 0.65, 0.65, 0)
        glBegin(GL_QUADS)

        glVertex3f(-10, -10, -2)
        glVertex3f(10, -10, -2)
        glVertex3f(10, 10, -2)
        glVertex3f(-10, 10, -2)
        glEnd()

        pygame.display.flip()
        pygame.time.wait(30)

    pygame.quit()

main()
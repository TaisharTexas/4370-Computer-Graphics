"""
COSC 4370 Homework #3
Andrew Lee's Submission for HW3

"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pywavefront
import numpy as np

# Rotation angle
rotationAngle = 0

class GeneralModel:
    def __init__(self, filename, calcOwnNormals):
        # class variables
        self.vertices = []
        self.faces = []
        self.normals = []
        self.textureCoords = []
        self.faceNormals = []
        self.faceTextures = []

        # load in the .obj file and prep it for rendering
        self.loadObjModel(filename)
        if calcOwnNormals:
            self.calcFaceNormals()

    def loadObjModel(self, filename):
        print("Parsing .obj file")
        with open(filename, 'r') as file:
            for eachLine in file:
                # skip comment and blank lines
                if eachLine.startswith('#') or not eachLine.strip():
                    continue

                #split line into component values
                lineVals = eachLine.split()

                # read vertex coords and append to vertex array
                if lineVals[0] == 'v':
                    x = float(lineVals[1])
                    y = float(lineVals[2])
                    z = float(lineVals[3])
                    self.vertices.append([x,y,z])

                # read facees and append to face array
                elif lineVals[0] == 'f':
                    temp = []
                    for vertexData in lineVals[1:]:
                        vertexIndex = int(vertexData.split('/')[0])
                        temp.append(vertexIndex - 1)

                    self.faces.append(temp)

                # identify but skip vertex normals -- can build out later
                elif lineVals[0] == 'vn':
                    continue
                # identify but skip vertex textures -- can build out later
                elif lineVals[0] == 'vt':
                    continue

    def calcFaceNormals(self):
        print("calculating face normals")

        #grab first three vertices of each face (following calc works for both quads and triangles)
        for eachFace in self.faces:
            v0 = np.array(self.vertices[eachFace[0]])
            v1 = np.array(self.vertices[eachFace[1]])
            v2 = np.array(self.vertices[eachFace[2]])

            #cross prod of two edge vectors gives the normal
            edge1 = v1-v0
            edge2 = v2-v0
            faceNorm = np.cross(edge1,edge2)

            length = np.linalg.norm(faceNorm)
            if length > 0:
                faceNorm = faceNorm/length
            self.faceNormals.append((faceNorm))

    def render(self):
        # print("rendering")
        for i, face in enumerate(self.faces):
            # uses the correct openGL call for quad or triagle
            if len(face) == 3:
                glBegin(GL_TRIANGLES)
            elif len(face) == 4:
                glBegin(GL_QUADS)
            else:
                #this shouldnt be used because I know the file is just triangles and quads, but its here for later if I finish this
                glBegin(GL_POLYGON)

            glNormal3fv(self.faceNormals[i])

            for vertexIndex in face:
                glVertex3fv(self.vertices[vertexIndex])

            glEnd()

def calculate_normal(v1, v2, v3):
    # Create vectors from the vertices
    vector1 = np.array(v2) - np.array(v1)
    vector2 = np.array(v3) - np.array(v1)
    normal = np.cross(vector1, vector2)

    # Normalize the vector
    length = np.linalg.norm(normal)
    if length > 0:
        normal = normal / length

    return normal

def load_obj(obj):
    display_list = glGenLists(1)
    glNewList(display_list, GL_COMPILE)

    glBegin(GL_TRIANGLES)

    # Iterate through each mesh in the object
    for mesh in obj.mesh_list:
        for face in mesh.faces:
            # Get vertices from the main vertices list
            vertices = []
            for vertex_index in face:
                vertex = obj.vertices[vertex_index]
                vertices.append(vertex)

            # Calculate normal for this face
            if len(vertices) >= 3:
                normal = calculate_normal(vertices[0], vertices[1], vertices[2])
                glNormal3fv(normal)

                # Draw the triangle
                for vertex in vertices:
                    glVertex3fv(vertex)

    glEnd()
    glEndList()

    return display_list


""" Toggles using the pywavefront library or the custom class loader that manually parses the obj file"""
    # true = use pywavefront (runs smoother)
    # false = use manual parser (runs way less efficiently)
def main(useLibrary):
    global rotationAngle

    # Initialize Pygame
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("HW3 Teapot with lights")

    # Set up perspective
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)

    # Setup lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Light properties
    light0_ambient = [0.0, 0.0, 0.0, 1.0]
    light0_diffuse = [1.0, 0.0, 0.0, 1.0]

    light1_ambient = [0.0, 0.0, 0.0, 1.0]
    light1_diffuse = [0.0, 0.0, 1.0, 1.0]

    # Light 0 - RED - down and right
    glLightfv(GL_LIGHT0, GL_AMBIENT, light0_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)

    # Light 1 - BLUE - up and left
    glLightfv(GL_LIGHT1, GL_AMBIENT, light1_ambient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)

    # Material properties
    material_shininess = [50.0]
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

    # Set teapot color
    glColor3f(1.0, 0.992, 0.816)

    teapot_display_list = None

    if useLibrary:
        # Load the teapot OBJ file w/ pywavefront
        print("Loading teapot.obj with pywavefront...")
        try:
            teapot = pywavefront.Wavefront('teapot.obj', collect_faces=True)
            print(f"Loaded teapot with {len(teapot.vertices)} vertices")
        except Exception as e:
            print(f"Error loading teapot.obj: {e}")
            print("Make sure teapot.obj is in the same directory as this script")
            return

        # Create display list for efficient rendering (precompute everything once)
        teapot_display_list = load_obj(teapot)
    else:
        print("Loading teapot.obj with manual class...")
        teapot = GeneralModel('teapot.obj', True)




    # Main loop
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Save the current matrix
        glPushMatrix()

        # Light position
        """ in frame:
        x: pos moves right, neg moves left
        y: pos moves up, neg moves down
        z: not super sure, the depth doesnt seem to work 
        w: 0 is a directional light (like a spotlight), 1 is a flood light (like a sun)
        """
        light0_pos = [5, -5, 0, .05] #red
        light1_pos = [-5, 5, 0, .07] #blue
        glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
        glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)

        glTranslatef(0.0, 0.0, -50.0)
        # Scale the teapot
        scale = 0.75
        glScalef(scale, scale, scale)

        # Tilt the teapot toward the camera and define how it'll rotate
        glRotatef(-55, 1, 0, 0)
        glRotatef(rotationAngle, 0, 0, 1)

        if useLibrary:
            glCallList(teapot_display_list)
        else:
            teapot.render()

        glPopMatrix()

        # Update rotation
        rotationAngle += 2.0
        if rotationAngle >= 360:
            rotationAngle -= 360

        # Update display
        pygame.display.flip()
        clock.tick(60)

    if useLibrary:
        # Clean up
        glDeleteLists(teapot_display_list, 1)
    pygame.quit()


if __name__ == "__main__":
    main(True)
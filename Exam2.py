"""
Write a program that simulates a particle fountain that sprays spherical particles from a cylindrical fountain.
Submit the code based on the requirements listed below..

Your code should meet the following requirements:

(10 pts.) Particles spawn from a cylinder fountain origin and follow ballistic trajectories with gravity applied.
(5 pts.) Initial velocities are randomized but can be increased or decreased within a range. (left/right keys)
(5 pts.) Particles spawn in a random cone and the cone angle can be changed with "<" and ">" keys within a range.
(5 pts.) Spawn rate is adjustable programmatically and clamped (I did 1000) to avoid runaway memory use. ("+"/"-" keys to increase or decrease the spawn rate.)
(10 pts) Shade or color the particles based on the lifetime of the particle remaining.
(5 pts.) Keypress rotates around the x-axis from 0 to 60 degrees (up/down keys).
(5 pts.) Provide lighting on the spheres from a light above the fountain.
(5 pts.) Move the camera in and out for a better view ("W" and "S" keys).

Some things you will find useful:

Pygame has a clock so you can get the elapsed time since the last update, that will be the delta time you need for the simulation.
The presentation from Lecture 19 will be useful, slide 20.
The formula will determine the vertical position of any particle based on the initial vertical velocity. The velocity in the other directions is constant.

"""

"""
Final Exam pt 2
Andrew Lee
note: you can probably tell I used claude to help cause no way I normally comment this good lol
    Pretty much I used claude to help me with the physics stuff (defining the separate fountain and particle classes 
    and using that to define current spawn and movement parameters for each particle and managing that)
    
    Also remember when I asked you about how to get text to draw on screen for the solar system homework and we decided not to try it? 
    Yeah so I got claude to help me with that a few weeks ago and its super nasty lol but it works (theres a version of this in my maze game too)

"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import random


class Particle:
    def __init__(self, position, velocity, lifetime):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt):
        """Update particle position using ballistic motion with gravity"""
        gravity = np.array([0.0, -9.8, 0.0])

        # p = p0 + v*t + 0.5*a*t^2
        self.position += self.velocity * dt + 0.5 * gravity * dt * dt
        self.velocity += gravity * dt
        self.age += dt

    def is_alive(self):
        return self.age < self.lifetime

    def get_color(self):
        """Color based on remaining lifetime (hot to cool)"""
        life_remaining = 1.0 - (self.age / self.lifetime)

        # Red (fresh )-> Yellow -> Green -> Blue (old)
        if life_remaining > 0.75:
            # Red to Yellow
            t = (life_remaining - 0.75) / 0.25
            return (1.0, 1.0 - t, 0.0)
        elif life_remaining > 0.5:
            # Yellow to Green
            t = (life_remaining - 0.5) / 0.25
            return (t, 1.0, 0.0)
        elif life_remaining > 0.25:
            # Green to Cyan
            t = (life_remaining - 0.25) / 0.25
            return (0.0, 1.0, 1.0 - t)
        else:
            # Cyan to Blue
            t = life_remaining / 0.25
            return (0.0, t, 1.0)


class ParticleFountain:
    def __init__(self):
        # Fountain parameters
        self.fountain_position = np.array([0.0, 0.0, 0.0])
        self.fountain_radius = 0.5

        # Particle parameters
        self.particles = []
        self.max_particles = 1000
        self.spawn_rate = 50  # particles per second
        self.accumulator = 0.0

        # Velocity parameters
        self.base_velocity = 8.0
        self.velocity_range = 2.0
        self.min_velocity = 5.0
        self.max_velocity = 15.0

        # Cone angle (in degrees)
        self.cone_angle = 30.0
        self.min_cone_angle = 10.0
        self.max_cone_angle = 80.0

        # Particle lifetime
        self.particle_lifetime = 3.0

        # Camera parameters
        self.camera_distance = 15.0
        self.camera_height = 5.0
        self.x_rotation = 30.0  # degrees

        # Sphere rendering
        self.quadric = gluNewQuadric()
        gluQuadricNormals(self.quadric, GLU_SMOOTH)

    def spawn_particle(self):
        """Spawn a new particle from the fountain"""
        # Random position on cylinder top
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, self.fountain_radius)
        pos_x = radius * math.cos(angle)
        pos_z = radius * math.sin(angle)

        """ tried to make them like come out from inside the cylinder by insetting the spawn"""
        position = [pos_x, 1.0, pos_z]

        # Random velocity in cone
        # Convert cone angle to radians
        cone_rad = math.radians(self.cone_angle)

        # Random angle from vertical (within cone)
        theta = random.uniform(0, cone_rad)
        # Random rotation around vertical axis
        phi = random.uniform(0, 2 * math.pi)

        # Random speed
        speed = self.base_velocity + random.uniform(-self.velocity_range, self.velocity_range)

        # Calculate velocity components
        vel_y = speed * math.cos(theta)  # vertical component
        horizontal_speed = speed * math.sin(theta)
        vel_x = horizontal_speed * math.cos(phi)
        vel_z = horizontal_speed * math.sin(phi)

        velocity = [vel_x, vel_y, vel_z]

        particle = Particle(position, velocity, self.particle_lifetime)
        self.particles.append(particle)

    def update(self, dt):
        """Update all particles and spawn new ones"""
        # Update existing particles
        self.particles = [p for p in self.particles if p.is_alive()]

        for particle in self.particles:
            particle.update(dt)

        # Spawn new particles based on spawn rate
        self.accumulator += dt
        particles_to_spawn = int(self.accumulator * self.spawn_rate)

        for _ in range(particles_to_spawn):
            if len(self.particles) < self.max_particles:
                self.spawn_particle()

        if particles_to_spawn > 0:
            self.accumulator -= particles_to_spawn / self.spawn_rate

    def draw_fountain(self):
        """Draw the cylindrical fountain base"""
        glPushMatrix()
        glColor3f(162/255, 202/255, 252/255)

        # Draw cylinder
        glTranslatef(0, -0.5, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(self.quadric, self.fountain_radius, self.fountain_radius, 1.5, 32, 1)

        # Draw top cap
        gluDisk(self.quadric, 0, self.fountain_radius, 32, 1)

        # Draw bottom cap
        glTranslatef(0, 0, 0.5)
        glRotatef(180, 1, 0, 0)
        gluDisk(self.quadric, 0, self.fountain_radius, 32, 1)

        glPopMatrix()

    def draw_particles(self):
        """Draw all particles as spheres"""
        for particle in self.particles:
            glPushMatrix()

            # Position
            glTranslatef(particle.position[0], particle.position[1], particle.position[2])

            # Color based on lifetime
            color = particle.get_color()
            glColor3f(*color)

            # Draw sphere
            gluSphere(self.quadric, 0.1, 16, 16)

            glPopMatrix()

    def render(self):
        """Render the entire scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Set up camera
        glTranslatef(0, 0, -self.camera_distance)
        glTranslatef(0, -self.camera_height, 0)
        glRotatef(self.x_rotation, 1, 0, 0)

        # Position light AFTER camera transformation so it stays in world space above fountain
        light_position = [0.0, 10.0, 0.0, 1.0]  # Positional light above fountain
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        # Draw fountain and particles
        self.draw_fountain()
        self.draw_particles()

    def adjust_velocity(self, increase):
        """Adjust base velocity"""
        if increase:
            self.base_velocity = min(self.base_velocity + 0.5, self.max_velocity)
        else:
            self.base_velocity = max(self.base_velocity - 0.5, self.min_velocity)
        print(f"vel: {self.base_velocity:.1f}")

    def adjust_cone_angle(self, increase):
        """Adjust cone angle"""
        if increase:
            self.cone_angle = min(self.cone_angle + 5.0, self.max_cone_angle)
        else:
            self.cone_angle = max(self.cone_angle - 5.0, self.min_cone_angle)
        print(f"angle: {self.cone_angle:.1f}°")

    def adjust_spawn_rate(self, increase):
        """Adjust spawn rate"""
        if increase:
            self.spawn_rate = min(self.spawn_rate + 10, 200)
        else:
            self.spawn_rate = max(self.spawn_rate - 10, 10)
        print(f"spawn: {self.spawn_rate} particles/sec")

    def adjust_x_rotation(self, increase):
        """Adjust x-axis rotation (0 to 60 degrees)"""
        if increase:
            self.x_rotation = min(self.x_rotation + 5.0, 60.0)
        else:
            self.x_rotation = max(self.x_rotation - 5.0, 0.0)
        print(f"x rot: {self.x_rotation:.1f}°")

    def adjust_camera_distance(self, move_in):
        """Move camera in or out"""
        if move_in:
            self.camera_distance = max(self.camera_distance - 1.0, 5.0)
        else:
            self.camera_distance = min(self.camera_distance + 1.0, 30.0)
        print(f"cam dist: {self.camera_distance:.1f}")

    def get_hud_info(self):
        """Return dictionary of current parameter values for HUD"""
        return {
            'velocity': self.base_velocity,
            'cone_angle': self.cone_angle,
            'spawn_rate': self.spawn_rate,
            'x_rotation': self.x_rotation,
            'camera_distance': self.camera_distance,
            'particle_count': len(self.particles)
        }


def setup_opengl():
    """Initialize OpenGL settings"""
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # LIGHTING
    light_ambient = [0.05, 0.05, 0.05, 1.0] # low ambient (I want some gray so its not complete dark in the shadows)
    light_diffuse = [1.5, 1.5, 1.5, 1.0] # strong diffuse for harsh light on balls
    light_specular = [1.0, 1.0, 1.0, 1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
    glClearColor(0.1, 0.1, 0.15, 1.0)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, 800 / 600, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


class TELEMETRY:
    """Telemetry for showing controls and current modifiers """

    """ they need a better way for drawing text on screen. They have circle and sphere and other shape functions why not a text print one?"""

    def __init__(self):
        # Initialize pygame font
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 22)

        self.bg_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)
        self.highlight_color = (100, 200, 255)

    def draw_text_opengl(self, text, x, y, font, color, screen_width, screen_height):
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        # Convert screen coordinates to OpenGL coordinates
        x_gl = x / screen_width * 2 - 1
        y_gl = 1 - y / screen_height * 2
        w_gl = text_surface.get_width() / screen_width * 2
        h_gl = text_surface.get_height() / screen_height * 2

        glColor4f(1, 1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1);
        glVertex2f(x_gl, y_gl)
        glTexCoord2f(1, 1);
        glVertex2f(x_gl + w_gl, y_gl)
        glTexCoord2f(1, 0);
        glVertex2f(x_gl + w_gl, y_gl - h_gl)
        glTexCoord2f(0, 0);
        glVertex2f(x_gl, y_gl - h_gl)
        glEnd()

        glDeleteTextures([texture_id])
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)

    def draw_background_box(self, x, y, width, height, screen_width, screen_height):
        """Draw semi-transparent background box"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Convert to OpenGL coordinates
        x_gl = x / screen_width * 2 - 1
        y_gl = 1 - y / screen_height * 2
        w_gl = width / screen_width * 2
        h_gl = height / screen_height * 2

        glColor4f(0, 0, 0, 0.7)
        glBegin(GL_QUADS)
        glVertex2f(x_gl, y_gl)
        glVertex2f(x_gl + w_gl, y_gl)
        glVertex2f(x_gl + w_gl, y_gl - h_gl)
        glVertex2f(x_gl, y_gl - h_gl)
        glEnd()

        glDisable(GL_BLEND)

    def render(self, fountain_info, screen_width, screen_height):
        """Render the HUD with controls and current values"""
        # Switch to orthographic projection for 2D overlay
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Disable depth test and lighting for HUD
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # Left panel - Controls
        left_x = 10
        left_y = 10
        panel_width = 280
        panel_height = 240

        self.draw_background_box(left_x, left_y, panel_width, panel_height, screen_width, screen_height)

        y_offset = left_y + 10
        line_height = 25

        self.draw_text_opengl("CONTROLS", left_x + 10, y_offset, self.font_large,
                              self.highlight_color, screen_width, screen_height)
        y_offset += line_height + 5

        controls = [
            "Left/Right : Velocity",
            "< > : Cone Angle",
            "+ - : Spawn Rate",
            "Up/Down : X Rotation",
            "W S : Camera Distance",
            "ESC : Exit"
        ]

        for control in controls:
            self.draw_text_opengl(control, left_x + 15, y_offset, self.font_small,
                                  self.text_color, screen_width, screen_height)
            y_offset += line_height

        # Right panel - Current Values
        right_x = screen_width - 250
        right_y = 10
        panel_width = 240
        panel_height = 200

        self.draw_background_box(right_x, right_y, panel_width, panel_height, screen_width, screen_height)

        y_offset = right_y + 10

        self.draw_text_opengl("CURRENT MODIFIERS", right_x + 10, y_offset, self.font_large,
                              self.highlight_color, screen_width, screen_height)
        y_offset += line_height + 5

        values = [
            f"Velocity: {fountain_info['velocity']:.1f}",
            f"Cone Angle: {fountain_info['cone_angle']:.1f}°",
            f"Spawn Rate: {fountain_info['spawn_rate']} /sec",
            f"X Rotation: {fountain_info['x_rotation']:.1f}°",
            f"Camera Dist: {fountain_info['camera_distance']:.1f}",
            f"Particles: {fountain_info['particle_count']}"
        ]

        for value in values:
            self.draw_text_opengl(value, right_x + 15, y_offset, self.font_small,
                                  self.text_color, screen_width, screen_height)
            y_offset += line_height

        # Restore 3D mode
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)


def main():
    pygame.init()
    display = (800, 600)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Particle Fountain Simulation")

    setup_opengl()

    fountain = ParticleFountain()
    telemetry = TELEMETRY()
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # end simulation
                    running = False
                elif event.key == pygame.K_LEFT: # reduce velocity modifier
                    fountain.adjust_velocity(False)
                elif event.key == pygame.K_RIGHT: # increase velocity modifier
                    fountain.adjust_velocity(True)
                elif event.key == pygame.K_COMMA:  # < - narrow spawn cone
                    fountain.adjust_cone_angle(False)
                elif event.key == pygame.K_PERIOD:  # > - widen spawn cone
                    fountain.adjust_cone_angle(True)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # + - increase spawn rate
                    fountain.adjust_spawn_rate(True)
                elif event.key == pygame.K_MINUS:  # - - decrease spawn rate
                    fountain.adjust_spawn_rate(False)
                elif event.key == pygame.K_UP: # rotate cam up
                    fountain.adjust_x_rotation(True)
                elif event.key == pygame.K_DOWN: # rotate cam down
                    fountain.adjust_x_rotation(False)
                elif event.key == pygame.K_w: # move closer to fountain
                    fountain.adjust_camera_distance(True)
                elif event.key == pygame.K_s: # move farther from fountain
                    fountain.adjust_camera_distance(False)

        # Update and render 3D scene
        fountain.update(dt)
        fountain.render()

        # Render HUD overlay
        fountain_info = fountain.get_hud_info()
        telemetry.render(fountain_info, display[0], display[1])

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
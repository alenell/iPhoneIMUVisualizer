import pygame
import csv
import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

#ALEX LENELL GYROSCOPE VISUALIZATION
#Uses values collected from Apple Iphone accelerometer and gyroscope

# Complementary filter coefficients
alpha = 0.98  # Weight for gyroscope data
beta = 1 - alpha  # Weight for accelerometer data
dt = 0.02  # Sample time (adjust as per your requirements)

roll,pitch,yaw = 0,0,0

# Initialize Pygame
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
glClearColor(1.0, 1.0, 1.0, 1.0)

# Set up the perspective
gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, 1000)

# Function to draw a cube
# Define vertices of the iPhone model
iphone_vertices = [
    (-0.5, 0.5, -0.1),  # Top left corner (front)
    (0.5, 0.5, -0.1),   # Top right corner (front)
    (0.5, -0.5, -0.1),  # Bottom right corner (front)
    (-0.5, -0.5, -0.1), # Bottom left corner (front)
    (-0.5, 0.5, 0.1),   # Top left corner (back)
    (0.5, 0.5, 0.1),    # Top right corner (back)
    (0.5, -0.5, 0.1),   # Bottom right corner (back)
    (-0.5, -0.5, 0.1),  # Bottom left corner (back)
]

# Define faces of the iPhone model
iphone_faces = [
    (0, 1, 2, 3),  # Front face
    (4, 5, 6, 7),  # Back face
    (0, 1, 5, 4),  # Top face
    (1, 2, 6, 5),  # Right face
    (2, 3, 7, 6),  # Bottom face
    (0, 3, 7, 4),  # Left face
]
# Define colors for each face of the iPhone model
iphone_colors = [
    (1, 0, 0),  # Front face (red)
    (0, 1, 0),  # Back face (green)
    (0, 0, 1),  # Top face (blue)
    (1, 1, 0),  # Right face (yellow)
    (1, 0, 1),  # Bottom face (magenta)
    (0, 1, 1),  # Left face (cyan)
]

# Function to draw the iPhone model with different colors for each face
def draw_iphone():
    for i, face in enumerate(iphone_faces):
        glColor3fv(iphone_colors[i])
        glBegin(GL_QUADS)
        for vertex_index in face:
            glVertex3fv(iphone_vertices[vertex_index])
        glEnd()

# Function to rotate the cube
def rotate_cube(yaw, pitch, roll):
    glLoadIdentity()  # Reset modelview matrix
    glRotatef(yaw, 0, 1, 0)
    glRotatef(pitch, 1, 0, 0)
    glRotatef(roll, 0, 0, 1)

yaw_values = []
pitch_values = []
roll_values = []

#CSV File with no header, [x,y,z,x_gyro,y_gyro,z_gyro]
file_sim = r''

with open(file_sim, 'r') as file:
    reader = csv.reader(file)
    i=0
    for row in reader:
        data=row
        ax, ay, az, gx, gy, gz = float(data[0]), float(data[1]), float(data[2]), float(data[3]), float(data[4]), float(data[5])        
        pitch_acc = math.atan2(ax, math.sqrt(ay**2 + az**2))
        roll_acc = math.atan2(-ay, -az)
        
        #Initial Orientation
        if i==0:
            pitch, roll = pitch_acc, roll_acc
        # Integrate gyroscope data
        roll += gx * dt
        pitch += gy * dt
        yaw += gz * dt
        
        # Apply complementary filter
        pitch = alpha * (pitch + gx * dt) + beta * pitch_acc
        roll = alpha * (roll + gy * dt) + beta * roll_acc
        
        yaw_values.append(float(yaw))
        pitch_values.append(float(pitch))
        roll_values.append(float(roll))
        i+=1

# Main loop
running = True
i = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    
    #glLoadIdentity()
    rotate_cube(yaw_values[i], pitch_values[i], roll_values[i])
    draw_iphone()

    pygame.display.flip()
    pygame.time.wait(20)  # Delay to control rotation speed

    i = (i + 1) % len(yaw_values)  # Loop back to the beginning of data

pygame.quit()






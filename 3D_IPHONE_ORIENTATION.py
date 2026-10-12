import csv
import math
import pygame
from OpenGL.GL import *
from OpenGL.GLU import *

alpha = 0.98
beta = 1 - alpha
dt = 0.02  # match your sensor's sample rate

file_sim = r'har_sample.csv'  # [ax, ay, az, gx, gy, gz], no header

# Accelerometer sign convention of the recording:
#   "har"    - gravity reads positive on the axis pointing up (UCI HAR / Samsung data)
#   "iphone" - gravity reads negative on the axis pointing up (iPhone Core Motion)
ACCEL_CONVENTION = "har"

# ---------- Precompute orientation ----------
yaw_values, pitch_values, roll_values = [], [], []
roll = pitch = yaw = 0.0

with open(file_sim, 'r') as f:
    for i, row in enumerate(csv.reader(f)):
        ax, ay, az, gx, gy, gz = map(float, row[:6])

        if ACCEL_CONVENTION == "har":
            pitch_acc = math.atan2(-ax, math.sqrt(ay**2 + az**2))
            roll_acc = math.atan2(ay, az)
        elif ACCEL_CONVENTION == "iphone":
            pitch_acc = math.atan2(ax, math.sqrt(ay**2 + az**2))
            roll_acc = math.atan2(-ay, -az)
        else:
            raise ValueError(f"Unknown ACCEL_CONVENTION: {ACCEL_CONVENTION!r}")

        if i == 0:
            pitch, roll = pitch_acc, roll_acc

        # Single integration, folded into the complementary filter
        roll = alpha * (roll + gx * dt) + beta * roll_acc
        pitch = alpha * (pitch + gy * dt) + beta * pitch_acc
        yaw += gz * dt

        yaw_values.append(math.degrees(yaw))
        pitch_values.append(math.degrees(pitch))
        roll_values.append(math.degrees(roll))

# ---------- Model (phone-shaped box) ----------
w, h, d = 0.4, 0.8, 0.05
vertices = [
    (-w, h, -d), (w, h, -d), (w, -h, -d), (-w, -h, -d),
    (-w, h, d),  (w, h, d),  (w, -h, d),  (-w, -h, d),
]
faces = [(0,1,2,3), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (0,3,7,4)]
colors = [(1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1), (0,1,1)]

def draw_iphone():
    glBegin(GL_QUADS)
    for face, color in zip(faces, colors):
        glColor3fv(color)
        for v in face:
            glVertex3fv(vertices[v])
    glEnd()

# ---------- Setup ----------
pygame.init()
display = (800, 600)
pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL)
glClearColor(1, 1, 1, 1)
glEnable(GL_DEPTH_TEST)

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
gluPerspective(45, display[0] / display[1], 0.1, 50.0)
glMatrixMode(GL_MODELVIEW)

# ---------- Main loop ----------
clock = pygame.time.Clock()
running = True
i = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0, 0, -4)               # camera back-off, every frame
    glRotatef(yaw_values[i],   0, 1, 0)
    glRotatef(pitch_values[i], 1, 0, 0)
    glRotatef(roll_values[i],  0, 0, 1)
    draw_iphone()

    pygame.display.flip()
    clock.tick(1 / dt)                   # 50 FPS to match dt
    i = (i + 1) % len(yaw_values)

pygame.quit()
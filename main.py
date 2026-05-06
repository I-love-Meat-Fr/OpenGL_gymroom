import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Camera state
cam_pos = [0.0, 1.7, 5.0] # 1.7m high (approx eye level)
cam_yaw = -90.0
cam_pitch = 0.0

first_mouse = True
last_x = 400
last_y = 300

keys_pressed = set()
quadric = None

def init_opengl():
    global quadric
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glEnable(GL_NORMALIZE)
    
    # Global ambient light
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.2, 0.2, 0.2, 1.0])

    # Setup ceiling lights
    setup_lights()

def setup_lights():
    # We will use 4 lights in the ceiling
    positions = [
        [-5.0, 4.9, -5.0, 1.0],
        [ 5.0, 4.9, -5.0, 1.0],
        [-5.0, 4.9,  5.0, 1.0],
        [ 5.0, 4.9,  5.0, 1.0]
    ]
    
    lights = [GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3]
    
    for i in range(4):
        glEnable(lights[i])
        glLightfv(lights[i], GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(lights[i], GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        # Attenuation to make it look like a room light
        glLightf(lights[i], GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(lights[i], GL_LINEAR_ATTENUATION, 0.05)
        glLightf(lights[i], GL_QUADRATIC_ATTENUATION, 0.01)

def apply_lights():
    positions = [
        [-5.0, 4.9, -5.0, 1.0],
        [ 5.0, 4.9, -5.0, 1.0],
        [-5.0, 4.9,  5.0, 1.0],
        [ 5.0, 4.9,  5.0, 1.0]
    ]
    lights = [GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3]
    for i in range(4):
        glLightfv(lights[i], GL_POSITION, positions[i])

def draw_solid_box(w, h, d):
    w /= 2.0; h /= 2.0; d /= 2.0
    glBegin(GL_QUADS)
    # Front Face
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-w, -h,  d); glVertex3f( w, -h,  d); glVertex3f( w,  h,  d); glVertex3f(-w,  h,  d)
    # Back Face
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(-w, -h, -d); glVertex3f(-w,  h, -d); glVertex3f( w,  h, -d); glVertex3f( w, -h, -d)
    # Top Face
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-w,  h, -d); glVertex3f(-w,  h,  d); glVertex3f( w,  h,  d); glVertex3f( w,  h, -d)
    # Bottom Face
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(-w, -h, -d); glVertex3f( w, -h, -d); glVertex3f( w, -h,  d); glVertex3f(-w, -h,  d)
    # Right face
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f( w, -h, -d); glVertex3f( w,  h, -d); glVertex3f( w,  h,  d); glVertex3f( w, -h,  d)
    # Left Face
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-w, -h, -d); glVertex3f(-w, -h,  d); glVertex3f(-w,  h,  d); glVertex3f(-w,  h, -d)
    glEnd()

def draw_room():
    # Floor (Dark grey rubber mat style)
    glColor3f(0.15, 0.15, 0.15)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-10, 0, -10); glVertex3f(-10, 0, 10); glVertex3f(10, 0, 10); glVertex3f(10, 0, -10)
    glEnd()
    
    # Ceiling (White)
    glColor3f(0.9, 0.9, 0.9)
    glBegin(GL_QUADS)
    glNormal3f(0, -1, 0)
    glVertex3f(-10, 5, -10); glVertex3f(10, 5, -10); glVertex3f(10, 5, 10); glVertex3f(-10, 5, 10)
    glEnd()

    # Walls (Light grey/blue)
    glColor3f(0.6, 0.7, 0.8)
    glBegin(GL_QUADS)
    # Back wall
    glNormal3f(0, 0, 1)
    glVertex3f(-10, 0, -10); glVertex3f(10, 0, -10); glVertex3f(10, 5, -10); glVertex3f(-10, 5, -10)
    # Front wall
    glNormal3f(0, 0, -1)
    glVertex3f(-10, 0, 10); glVertex3f(-10, 5, 10); glVertex3f(10, 5, 10); glVertex3f(10, 0, 10)
    # Left wall
    glNormal3f(1, 0, 0)
    glVertex3f(-10, 0, -10); glVertex3f(-10, 5, -10); glVertex3f(-10, 5, 10); glVertex3f(-10, 0, 10)
    # Right wall (Mirror)
    glColor3f(0.8, 0.9, 1.0) # slightly reflective looking
    glNormal3f(-1, 0, 0)
    glVertex3f(10, 0, -10); glVertex3f(10, 0, 10); glVertex3f(10, 5, 10); glVertex3f(10, 5, -10)
    glEnd()

    # Light fixtures
    glDisable(GL_LIGHTING) # draw bright white so they look like sources
    glColor3f(1.0, 1.0, 1.0)
    positions = [
        [-5.0, 4.95, -5.0], [5.0, 4.95, -5.0],
        [-5.0, 4.95, 5.0], [5.0, 4.95, 5.0]
    ]
    for p in positions:
        glPushMatrix()
        glTranslatef(p[0], p[1], p[2])
        draw_solid_box(2.0, 0.1, 1.0)
        glPopMatrix()
    glEnable(GL_LIGHTING)

def draw_bench_press(x, y, z, rot_y):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rot_y, 0, 1, 0)
    
    # Bench pad
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 0.5, 0)
    draw_solid_box(0.4, 0.1, 1.4)
    glPopMatrix()
    
    # Rack posts (4 pillars)
    glColor3f(0.5, 0.5, 0.5)
    
    # Front pillars
    glPushMatrix()
    glTranslatef(-0.25, 0.6, -0.6)
    draw_solid_box(0.1, 1.2, 0.1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.25, 0.6, -0.6)
    draw_solid_box(0.1, 1.2, 0.1)
    glPopMatrix()
    
    # Back pillars
    glPushMatrix()
    glTranslatef(-0.25, 0.4, 0.4)
    draw_solid_box(0.1, 0.8, 0.1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.25, 0.4, 0.4)
    draw_solid_box(0.1, 0.8, 0.1)
    glPopMatrix()
    
    # Barbell
    glColor3f(0.8, 0.8, 0.8)
    glPushMatrix()
    glTranslatef(-0.8, 1.25, -0.6)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quadric, 0.02, 0.02, 1.6, 10, 1)
    glPopMatrix()
    
    # Weights
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(-0.7, 1.25, -0.6)
    glRotatef(90, 0, 1, 0)
    gluDisk(quadric, 0.02, 0.2, 20, 1)
    glTranslatef(0, 0, 1.4)
    gluDisk(quadric, 0.02, 0.2, 20, 1)
    glPopMatrix()
    
    glPopMatrix()

def draw_treadmill(x, y, z, rot_y):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rot_y, 0, 1, 0)
    
    # Base/Belt
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 0.15, 0)
    draw_solid_box(0.8, 0.1, 2.0)
    glPopMatrix()
    
    # Front posts
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(-0.35, 0.7, -0.9)
    draw_solid_box(0.1, 1.2, 0.1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.35, 0.7, -0.9)
    draw_solid_box(0.1, 1.2, 0.1)
    glPopMatrix()
    
    # Display console
    glColor3f(0.05, 0.05, 0.05)
    glPushMatrix()
    glTranslatef(0, 1.3, -0.85)
    glRotatef(-30, 1, 0, 0)
    draw_solid_box(0.9, 0.4, 0.1)
    glPopMatrix()
    
    glPopMatrix()

def draw_dumbbell_rack(x, y, z, rot_y):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rot_y, 0, 1, 0)
    
    # Shelves
    glColor3f(0.3, 0.3, 0.3)
    for h in [0.4, 0.8]:
        glPushMatrix()
        glTranslatef(0, h, 0)
        glRotatef(20, 1, 0, 0)
        draw_solid_box(3.0, 0.05, 0.4)
        glPopMatrix()
    
    # Side supports
    glPushMatrix()
    glTranslatef(-1.5, 0.5, 0)
    draw_solid_box(0.1, 1.0, 0.5)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(1.5, 0.5, 0)
    draw_solid_box(0.1, 1.0, 0.5)
    glPopMatrix()
    
    # Dumbbells on top shelf
    for i in range(-5, 6):
        glPushMatrix()
        glTranslatef(i * 0.25, 0.85, 0)
        glColor3f(0.7, 0.7, 0.7)
        # Handle
        glPushMatrix()
        glTranslatef(-0.1, 0, 0)
        glRotatef(90, 0, 1, 0)
        gluCylinder(quadric, 0.015, 0.015, 0.2, 10, 1)
        glPopMatrix()
        # Weights
        glColor3f(0.1, 0.1, 0.1)
        
        # Left Weight
        glPushMatrix()
        glTranslatef(-0.14, 0, 0)
        glRotatef(90, 0, 1, 0)
        gluDisk(quadric, 0.015, 0.08, 10, 1)
        gluCylinder(quadric, 0.08, 0.08, 0.04, 10, 1)
        glTranslatef(0, 0, 0.04)
        gluDisk(quadric, 0.015, 0.08, 10, 1)
        glPopMatrix()
        
        # Right Weight
        glPushMatrix()
        glTranslatef(0.1, 0, 0)
        glRotatef(90, 0, 1, 0)
        gluDisk(quadric, 0.015, 0.08, 10, 1)
        gluCylinder(quadric, 0.08, 0.08, 0.04, 10, 1)
        glTranslatef(0, 0, 0.04)
        gluDisk(quadric, 0.015, 0.08, 10, 1)
        glPopMatrix()
        
        # Pop the dumbbell matrix
        glPopMatrix()
        
    glPopMatrix()

def key_callback(window, key, scancode, action, mods):
    global keys_pressed
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
        
    if action == glfw.PRESS:
        keys_pressed.add(key)
    elif action == glfw.RELEASE:
        if key in keys_pressed:
            keys_pressed.remove(key)

def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y, cam_yaw, cam_pitch
    
    if first_mouse:
        last_x = xpos
        last_y = ypos
        first_mouse = False
        
    xoffset = xpos - last_x
    yoffset = last_y - ypos
    last_x = xpos
    last_y = ypos
    
    sensitivity = 0.1
    xoffset *= sensitivity
    yoffset *= sensitivity
    
    cam_yaw += xoffset
    cam_pitch += yoffset
    
    if cam_pitch > 89.0:
        cam_pitch = 89.0
    if cam_pitch < -89.0:
        cam_pitch = -89.0

def process_input(dt):
    global cam_pos, cam_yaw
    move_speed = 4.0 * dt
    
    yaw_rad = math.radians(cam_yaw)
    forward_x = math.sin(yaw_rad)
    forward_z = -math.cos(yaw_rad)
    right_x = math.cos(yaw_rad)
    right_z = math.sin(yaw_rad)

    # Calculate requested movement
    dx, dy, dz = 0, 0, 0
    if glfw.KEY_W in keys_pressed:
        dx += forward_x * move_speed
        dz += forward_z * move_speed
    if glfw.KEY_S in keys_pressed:
        dx -= forward_x * move_speed
        dz -= forward_z * move_speed
    if glfw.KEY_A in keys_pressed:
        dx -= right_x * move_speed
        dz -= right_z * move_speed
    if glfw.KEY_D in keys_pressed:
        dx += right_x * move_speed
        dz += right_z * move_speed
        
    # Apply movement with simple collision against walls (Room is 20x20, so -10 to 10)
    new_x = cam_pos[0] + dx
    new_z = cam_pos[2] + dz
    
    if -9.5 < new_x < 9.5:
        cam_pos[0] = new_x
    if -9.5 < new_z < 9.5:
        cam_pos[2] = new_z

def main():
    if not glfw.init():
        return

    window = glfw.create_window(1024, 768, "OpenGL 3D Space - Gym Room", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_key_callback(window, key_callback)

    init_opengl()

    glMatrixMode(GL_PROJECTION)
    gluPerspective(60.0, 1024.0/768.0, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time

        process_input(dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glRotatef(-cam_pitch, 1, 0, 0)
        glRotatef(cam_yaw, 0, 1, 0) 
        
        glTranslatef(-cam_pos[0], -cam_pos[1], -cam_pos[2])

        # Make sure lights stay in world space
        apply_lights()

        # Draw the environment
        draw_room()
        
        # Draw some gym equipment
        
        # Row of treadmills looking out the "front"
        for i in range(-3, 4, 2):
            draw_treadmill(i, 0, -8, 0)
            
        # Dumbbell rack against the left wall
        draw_dumbbell_rack(-9, 0, 0, 90)
        
        # A few bench presses in the middle
        draw_bench_press(-3, 0, 0, 0)
        draw_bench_press(3, 0, 0, 0)
        draw_bench_press(-3, 0, 4, 0)
        draw_bench_press(3, 0, 4, 0)

        glfw.swap_buffers(window)
        glfw.poll_events()

    if quadric:
        gluDeleteQuadric(quadric)
    glfw.terminate()

if __name__ == "__main__":
    main()

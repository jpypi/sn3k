#!/usr/bin/env python

import sys
import math
import itertools
import random
from threading import Thread

import pyglet
from pyglet.gl import *
from pyglet.window import key

#import piglib
from d3primatives import *
from player import Player


# Create a window object
window = pyglet.window.Window(800, 550, "Snek!")
#window.set_vsync(True)

keyboard = key.KeyStateHandler()
window.push_handlers(keyboard)

glClearColor(.2,.2,.2,1)
glEnable(GL_DEPTH_TEST)

#glEnable(GL_LIGHTING)
#glEnable(GL_COLOR_MATERIAL)
#
#glEnable(GL_LIGHT0)
#glLightfv(GL_LIGHT0, GL_AMBIENT, *map(GLfloat,(0,0,0,1)))
#glLightfv(GL_LIGHT0, GL_DIFFUSE, *map(GLfloat,(1,1,1,1)))
#glLightfv(GL_LIGHT0, GL_SPECULAR, *map(GLfloat,(1,1,1,1)))
#glLightfv(GL_LIGHT0, GL_POSITION, *map(GLfloat,(1,-1,0,0)))
#glLightfv(GL_LIGHT0, GL_LINEAR_ATTENUATION, GLfloat(0.8))
#glLightModelfv(GL_LIGHT_MODEL_AMBIENT, *map(GLfloat,(0.2,0.2,0.2,1)))
##glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, *map(GLfloat,(0,0,1,0)))
#glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
#glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, *map(GLfloat,(0,1,1,1)))
#glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, *map(GLfloat,(0,0,0,1)))

helv_font=pyglet.font.load("Helvetica", 14)
fps_display = pyglet.clock.ClockDisplay(helv_font, color=(1, 0, 0, 0.3))

fov = 65 #40
world_size = 800
n_food = 4
snakes = {0: Player([0, 0, -400])}
player = snakes[0]

import socket
import struct
from network_utils import *
DEBUG = False
ERR_PREFIX = "** Error: "

def network_update():
    s = socket.socket()
    host = "perplexed.duckdns.org"
    try:
        s.connect((host, 4588))
    except socket.error as e:
        # 61 is unreachable
        if e.errno == 61:
            print(ERR_PREFIX + "Could not connect to '%s'"%host)
        else:
            print(e)
        return


    # Initial handshake
    s.send(struct.pack(">ii", GIVE_ID, GIVE_ID_N))
    d = s.recv(4)
    my_id = struct.unpack(">i", d)[0]
    print("My id is: {%d}"%my_id)

    while NETWORKING_ACTIVE:
        if DEBUG: print("Going")
        tail = player.tail[:]
        header = struct.pack(">ii", my_id, len(tail))
        data = ""
        for block in tail:
            data += struct.pack(">iiii", TAIL_BLOCK, *map(int, block.pos))
        if DEBUG: print("Sending my data")
        s.sendall(header+data)

        if DEBUG: print("Recieving n for udo")
        n_user_data_objects = struct.unpack(">i", s.recv(4))[0]
        if DEBUG: print("n = %d"%n_user_data_objects)

        last_ids = []
        for i in xrange(n_user_data_objects):
            if DEBUG: print("Recieving header")
            user_id, n_objs = RecieveHeader(s)
            if DEBUG: print("uid: %d, n_objs: %d"%(user_id, n_objs))
            # No need to try to recieve objects if there aren't any coming
            if n_objs:
                if DEBUG: print("Recieving %d objects"%n_objs)
                values = RecieveObjects(s, n_objs)
                if user_id != my_id:
                    last_ids.append(user_id)
                    sn = snakes.setdefault(user_id,
                            Player([0,0,0], network_player=True))
                    sn.tail = map(lambda v: Cube([v[1],v[2],v[3]], 10), values)

        # Clean up old, dead snakes
        for key in snakes.keys():
            if key != 0 and key not in last_ids:
                del snakes[key]


    s.close()


NETWORKING_ACTIVE = True
t = Thread(target=network_update)
t.start()

@window.event
def on_close():
    global NETWORKING_ACTIVE
    NETWORKING_ACTIVE = False


# Use a decorater to register a custom action for the on_draw event
@window.event
def on_draw():
    # Clear the current GL Window
    window.clear()
    #fps_display.draw()

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    dead = []
    pos = map(lambda x: -x, player.pos)

    for i,c in enumerate(food):
        if c.collidePoint(pos):
            dead.append(i)
            player.ateFood()
        else:
            glPushMatrix()
            glRotatef(c.angle[0], 1, 0, 0)
            glRotatef(c.angle[1], 0, 1, 0)
            glRotatef(c.angle[2], 0, 0, 1)
            glTranslatef(*c.pos)
            glBegin(GL_QUADS)
            c.draw()
            glEnd()
            glPopMatrix()

    for i,iv in enumerate(dead):
        AddRandomFood()
        del food[iv-i]

    for snake in snakes.values():
        snake.draw()

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glColor3f(1,1,1)
    glLineWidth(2)
    glBegin(GL_QUADS)
    world_box.draw()
    glEnd()

    #glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    #glBegin(GL_QUADS)
    ##glMaterialfv(GL_FRONT_AND_BACK,GL_AMBIENT, GLfloat(0.2),GLfloat(0.2),GLfloat(0.2),GLfloat(1))
    #world_box.draw()
    #glEnd()

    glPointSize(2)
    glColor3f(1,1,1)
    glBegin(GL_POINTS)
    for l in points:
        glVertex3f(*l)
    glEnd()


@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    aspect_ratio = width / height
    gluPerspective(fov, aspect_ratio, 1, 2000)

    return pyglet.event.EVENT_HANDLED


def do_view_state():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glRotatef(player.angle[0], 1, 0, 0)
    glRotatef(player.angle[1], 0, 1, 0)
    glTranslatef(*player.pos)


def euclidean_dist(v1, v2):
    value = 0
    for i in range(3):
        value += (v1[i] - v2[i]) ** 2

    return math.sqrt(value)


def move_facing(dist):
    horiz_ang = math.radians(-player.angle[1])
    xh = math.sin(horiz_ang) * dist
    zh = math.cos(horiz_ang) * dist

    vert_ang = math.radians(player.angle[0])
    yv = math.sin(vert_ang) * dist

    player.pos[0] += xh
    player.pos[1] += yv
    player.pos[2] += zh

    player.pos[0] = (player.pos[0] >  world_size and  world_size) or\
                    (player.pos[0] < -world_size and -world_size) or player.pos[0]
    player.pos[1] = (player.pos[1] >  world_size and  world_size) or\
                    (player.pos[1] < -world_size and -world_size) or player.pos[1]
    player.pos[2] = (player.pos[2] >  world_size and  world_size) or\
                    (player.pos[2] < -world_size and -world_size) or player.pos[2]

    # Update the player's tail (add new point and remove from end)
    pos = map(lambda x: -x, player.pos)
    if not player.tail or euclidean_dist(pos, player.tail[0].pos) > player.chunk_dist:
        player.tail.insert(0, Cube(pos, 10))
        if len(player.tail) > player.length:
            player.tail.pop()

    do_view_state()


def main_update(dt):
    #global fov
    #if keyboard[key.Y]:
    #    fov += 1
    #    print(fov)
    #    on_resize(window.width, window.height)
    #if keyboard[key.U]:
    #    fov -= fov > 1
    #    print(fov)
    #    on_resize(window.width, window.height)

    #if keyboard[key.SPACE]:
    move_facing(player.move_rate*dt)

    if keyboard[key.W]:
        player.angle[0] -= (player.angle[0] > -50)*dt*player.rotation_rate[0]
        do_view_state()

    if keyboard[key.S]:
        player.angle[0] += (player.angle[0] < 60)*dt*player.rotation_rate[0]
        do_view_state()

    if keyboard[key.A]:
        player.angle[1] -= dt*player.rotation_rate[1]
        do_view_state()

    if keyboard[key.D]:
        player.angle[1] += dt*player.rotation_rate[1]
        do_view_state()


food_colors = (
            ( 0,  1,  0),
            ( 0, .5,  0),
            ( 0,  1,  0),
            ( 0, .5,  0),
            ( 1,  0,  0),
            (.5,  0,  0),
            ( 1,  0,  0),
            (.5,  0,  0),
            (.6,  1,  0),
            (.5, .5,  0),
            (.6,  1,  0),
            (.5, .5,  0)
        )
food = []
padding = 50
def AddRandomFood():
    x = random.randrange(-world_size+padding, world_size-padding)
    y = random.randrange(-world_size+padding, world_size-padding)
    z = random.randrange(-world_size+padding, world_size-padding)
    c = Cube((x, y, z), 20)
    c.colors = food_colors
    food.append(c)

for _ in xrange(n_food):
    AddRandomFood()

# Define the world space
world_box = Cube((0,0,0), world_size)
world_box.colors = ((0.7,0.7,0.7), (0.4, 0.4, 0.4))*6

# Define a nice point grid so people don't get sick or lost/confused
points = []
world_grid_size = world_size
step = 200
for x in range(-world_grid_size, world_grid_size, step):
    for z in range(-world_grid_size, world_grid_size, step):
        for y in range(-world_grid_size, world_grid_size, step):
            points.append((x,y,z))

pyglet.clock.schedule_interval(main_update, 1/60.0)

do_view_state()
pyglet.app.run()



#window.push_handlers(pyglet.window.event.WindowEventLogger())
#@window.event
#def on_text_motion(motion):
#    pass

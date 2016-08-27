from pyglet.gl import glColor3f, glVertex3f


__all__ = ["Cube"]


class Cube():
    def __init__(self, pos, size, angle=[0, 0, 0]):
        self.size = size
        self.pos = pos
        self.angle = angle
        self.colors = [
                (1,0,0),
                (0.5,0,0),
                (0,0,1),
                (0,0,0.5),
                (1,1,0),
                (0.5,0.5,0),
                (0,1,0),
                (0,0.5,0),
                (1,0,1),
                (0.5,0,0.5),
                (0,1,1),
                (0,0.5,0.5)
                ]

    def draw(self):
        #glLoadIdentity()
        #glTranslatef(*self.pos)
        #glColor3ub(255, 255, 0)

        # Front
        glColor3f(*self.colors[0])
        glVertex3f(-self.size, self.size, self.size)
        glVertex3f( self.size, self.size, self.size)
        glColor3f(*self.colors[1])
        glVertex3f( self.size,-self.size, self.size)
        glVertex3f(-self.size,-self.size, self.size)

        # Back
        glColor3f(*self.colors[2])
        glVertex3f(-self.size, self.size,-self.size)
        glVertex3f( self.size, self.size,-self.size)
        glColor3f(*self.colors[3])
        glVertex3f( self.size,-self.size,-self.size)
        glVertex3f(-self.size,-self.size,-self.size)

        # Top
        glColor3f(*self.colors[4])
        glVertex3f(-self.size, self.size, self.size)
        glVertex3f( self.size, self.size, self.size)
        glColor3f(*self.colors[5])
        glVertex3f( self.size, self.size,-self.size)
        glVertex3f(-self.size, self.size,-self.size)

        # Bottom
        glColor3f(*self.colors[6])
        glVertex3f(-self.size,-self.size, self.size)
        glVertex3f( self.size,-self.size, self.size)
        glColor3f(*self.colors[7])
        glVertex3f( self.size,-self.size,-self.size)
        glVertex3f(-self.size,-self.size,-self.size)

        # Left
        glColor3f(*self.colors[8])
        glVertex3f(-self.size, self.size, self.size)
        glVertex3f(-self.size, self.size,-self.size)
        glColor3f(*self.colors[9])
        glVertex3f(-self.size,-self.size,-self.size)
        glVertex3f(-self.size,-self.size, self.size)

        # Right
        glColor3f(*self.colors[10])
        glVertex3f( self.size, self.size, self.size)
        glVertex3f( self.size, self.size,-self.size)
        glColor3f(*self.colors[11])
        glVertex3f( self.size,-self.size,-self.size)
        glVertex3f( self.size,-self.size, self.size)

    def collidePoint(self, vec3):
        collision = True

        for i in xrange(3):
            collision &= (self.pos[i] - self.size) < vec3[i] < (self.pos[i] + self.size)

        return collision

    def __repr__(self):
        return "<Cube((%d, %d, %d))>"%(self.pos[0], self.pos[1], self.pos[2])

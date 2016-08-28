from pyglet.gl import glPushMatrix, glRotatef, glTranslatef,\
                      glBegin, glEnd, glPopMatrix, GL_QUADS


__all__ = ["Player"]


class Player:
    def __init__(self, pos, angle=[0, 0, 0], network_player = False):
        self.pos = pos
        self.angle = angle
        # Length is always +1 so that when not drawing the first box it's the
        # right length
        self.network_player = network_player
        self.initial_length = 21
        self.length = self.initial_length
        self.tail = []
        self.rotation_rate = [60, 70]
        self.move_rate = 330
        self.chunk_dist = 30

    def getSize(self):
        return self.length - 1

    def ateFood(self):
        self.length += 5
        print(self.getSize())

    @property
    def inv_pos(self):
        return map(lambda x: -x, self.pos)

    def draw(self):
        # Draw all but the first segment so that it's not drawing right on
        p = self.inv_pos
        for c in self.tail[1:]:
            if c.collidePoint(p):
                self.length = self.initial_length
                self.tail = self.tail[:self.length]
                print("YOU ATE YOURSELF!")
                break


            glPushMatrix()
            glRotatef(c.angle[0], 1, 0, 0)
            glRotatef(c.angle[1], 0, 1, 0)
            glRotatef(c.angle[2], 0, 0, 1)
            glTranslatef(*c.pos)
            glBegin(GL_QUADS)
            c.draw()
            glEnd()
            glPopMatrix()

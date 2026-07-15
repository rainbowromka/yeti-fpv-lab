from OpenGL.GL import *

class GridPlane:
    def __init__(self, axis, color=(0.5, 0.5, 0.5)):
        self.axis = axis
        self.color = color
        self.size = 1000.0

    def draw(self):
        glColor4f(self.color[0], self.color[1], self.color[2], 0.5)

        s = self.size

        if self.axis == 'xy':
            glNormal3f(0, 0, 1)  # нормаль вдоль Z
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0); glVertex3f(s, 0, 0); glVertex3f(0, s, 0)
            glVertex3f(s, 0, 0); glVertex3f(s, s, 0); glVertex3f(0, s, 0)
            glEnd()

        elif self.axis == 'xz':
            glNormal3f(0, 1, 0)  # нормаль вдоль Y
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0); glVertex3f(s, 0, 0); glVertex3f(0, 0, s)
            glVertex3f(s, 0, 0); glVertex3f(s, 0, s); glVertex3f(0, 0, s)
            glEnd()

        elif self.axis == 'yz':
            glNormal3f(1, 0, 0)  # нормаль вдоль X
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0); glVertex3f(0, s, 0); glVertex3f(0, 0, s)
            glVertex3f(0, s, 0); glVertex3f(0, s, s); glVertex3f(0, 0, s)
            glEnd()
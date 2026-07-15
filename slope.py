from OpenGL.GL import *

class Slope:
    def __init__(self):
        self.x_start = 250.0
        self.y_start = 250.0
        self.z = 250.0
        self.length = 1400.0
        self.width = 200.0

    def draw(self):
        glColor3f(1.0, 1.0, 1.0)
        glNormal3f(0, 0, 1)  # нормаль вдоль Z

        x1 = self.x_start
        y1 = self.y_start
        x2 = self.x_start + self.length
        y2 = self.y_start + self.width

        glBegin(GL_TRIANGLES)
        glVertex3f(x1, y1, self.z)
        glVertex3f(x2, y1, self.z)
        glVertex3f(x1, y2, self.z)
        
        glVertex3f(x2, y1, self.z)
        glVertex3f(x2, y2, self.z)
        glVertex3f(x1, y2, self.z)
        glEnd()
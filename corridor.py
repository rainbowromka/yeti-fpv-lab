import random
from OpenGL.GL import *

class Corridor:
    def __init__(self):
        self.x_start = 250.0
        self.y_center = 350.0
        self.z_base = 250.0
        self.height = 20.0
        self.length = 1400.0
        self.segments = 20
        self.min_width = 50.0
        self.max_width = 120.0
        self.texture = None

        self.generate()

    def create_texture(self):
        size = 64
        pixels = []
        for y in range(size):
            for x in range(size):
                if (x // 8) % 2 == (y // 8) % 2:
                    pixels.extend([20, 80, 20])
                else:
                    pixels.extend([40, 140, 40])
    
        tex = GLuint()
        ctypes.cdll.LoadLibrary('libGL.so.1').glGenTextures(1, ctypes.byref(tex))
        self.texture = tex.value
    
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, size, size, 0, GL_RGB, GL_UNSIGNED_BYTE, bytes(pixels))
        
        # Mipmapping
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    def generate(self):
        seg_len = self.length / self.segments

        self.left_points = []
        self.right_points = []
        self.center_line = []  # центральная линия
        
        current_x = self.x_start

        for i in range(self.segments + 1):
            center_offset = random.uniform(-40, 40)
            half_width = random.uniform(self.min_width / 2, self.max_width / 2)

            center_y = self.y_center + center_offset
            left_y = center_y - half_width
            right_y = center_y + half_width

            self.left_points.append((current_x, left_y))
            self.right_points.append((current_x, right_y))
            self.center_line.append((current_x, center_y))
            
            current_x += seg_len

    def draw(self):
        if self.texture is None:
            self.create_texture()
        
        z_top = self.z_base + self.height
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
        # Масштаб текстуры: квадрат 2x2 метра
        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glScalef(1/8, 1/8, 1.0)
        glMatrixMode(GL_MODELVIEW)

        # ========== Стены коридора ==========
        for i in range(self.segments):
            lx1, ly1 = self.left_points[i]
            lx2, ly2 = self.left_points[i + 1]
            rx1, ry1 = self.right_points[i]
            rx2, ry2 = self.right_points[i + 1]

            # Левая стена
            dx = lx2 - lx1
            dy = ly2 - ly1
            n_len = (dx*dx + dy*dy) ** 0.5
            if n_len > 0:
                glNormal3f(dy/n_len, -dx/n_len, 0)

            glBegin(GL_QUADS)
            glTexCoord2f(lx1, self.z_base); glVertex3f(lx1, ly1, self.z_base)
            glTexCoord2f(lx2, self.z_base); glVertex3f(lx2, ly2, self.z_base)
            glTexCoord2f(lx2, z_top); glVertex3f(lx2, ly2, z_top)
            glTexCoord2f(lx1, z_top); glVertex3f(lx1, ly1, z_top)
            glEnd()

            # Правая стена
            dx = rx2 - rx1
            dy = ry2 - ry1
            n_len = (dx*dx + dy*dy) ** 0.5
            if n_len > 0:
                glNormal3f(-dy/n_len, dx/n_len, 0)

            glBegin(GL_QUADS)
            glTexCoord2f(rx1, self.z_base); glVertex3f(rx1, ry1, self.z_base)
            glTexCoord2f(rx2, self.z_base); glVertex3f(rx2, ry2, self.z_base)
            glTexCoord2f(rx2, z_top); glVertex3f(rx2, ry2, z_top)
            glTexCoord2f(rx1, z_top); glVertex3f(rx1, ry1, z_top)
            glEnd()
    
        # ========== Левый лес ==========
        y_edge = 250.0

        for i in range(self.segments):
            lx1, ly1 = self.left_points[i]
            lx2, ly2 = self.left_points[i + 1]

            # Крыша
            glNormal3f(0, 0, -1)
            glBegin(GL_TRIANGLES)
            glTexCoord2f(lx1, ly1); glVertex3f(lx1, ly1, z_top)
            glTexCoord2f(lx1, y_edge); glVertex3f(lx1, y_edge, z_top)
            glTexCoord2f(lx2, ly2); glVertex3f(lx2, ly2, z_top)

            glTexCoord2f(lx2, ly2); glVertex3f(lx2, ly2, z_top)
            glTexCoord2f(lx1, y_edge); glVertex3f(lx1, y_edge, z_top)
            glTexCoord2f(lx2, y_edge); glVertex3f(lx2, y_edge, z_top)
            glEnd()

            # Боковая стена
            glNormal3f(0, 1, 0)
            glBegin(GL_QUADS)
            glTexCoord2f(lx1, self.z_base); glVertex3f(lx1, y_edge, self.z_base)
            glTexCoord2f(lx2, self.z_base); glVertex3f(lx2, y_edge, self.z_base)
            glTexCoord2f(lx2, z_top); glVertex3f(lx2, y_edge, z_top)
            glTexCoord2f(lx1, z_top); glVertex3f(lx1, y_edge, z_top)
            glEnd()

        # Торцы левого леса
        lx, ly = self.left_points[0]
        glNormal3f(1, 0, 0)
        glBegin(GL_QUADS)
        glTexCoord2f(ly, self.z_base); glVertex3f(lx, ly, self.z_base)
        glTexCoord2f(y_edge, self.z_base); glVertex3f(lx, y_edge, self.z_base)
        glTexCoord2f(y_edge, z_top); glVertex3f(lx, y_edge, z_top)
        glTexCoord2f(ly, z_top); glVertex3f(lx, ly, z_top)
        glEnd()

        lx, ly = self.left_points[-1]
        glNormal3f(-1, 0, 0)
        glBegin(GL_QUADS)
        glTexCoord2f(ly, self.z_base); glVertex3f(lx, ly, self.z_base)
        glTexCoord2f(y_edge, self.z_base); glVertex3f(lx, y_edge, self.z_base)
        glTexCoord2f(y_edge, z_top); glVertex3f(lx, y_edge, z_top)
        glTexCoord2f(ly, z_top); glVertex3f(lx, ly, z_top)
        glEnd()
    
        # ========== Правый лес ==========
        y_edge = 450.0

        for i in range(self.segments):
            rx1, ry1 = self.right_points[i]
            rx2, ry2 = self.right_points[i + 1]

            # Крыша
            glNormal3f(0, 0, -1)
            glBegin(GL_TRIANGLES)
            glTexCoord2f(rx1, ry1); glVertex3f(rx1, ry1, z_top)
            glTexCoord2f(rx1, y_edge); glVertex3f(rx1, y_edge, z_top)
            glTexCoord2f(rx2, ry2); glVertex3f(rx2, ry2, z_top)

            glTexCoord2f(rx2, ry2); glVertex3f(rx2, ry2, z_top)
            glTexCoord2f(rx1, y_edge); glVertex3f(rx1, y_edge, z_top)
            glTexCoord2f(rx2, y_edge); glVertex3f(rx2, y_edge, z_top)
            glEnd()

            # Боковая стена
            glNormal3f(0, -1, 0)
            glBegin(GL_QUADS)
            glTexCoord2f(rx1, self.z_base); glVertex3f(rx1, y_edge, self.z_base)
            glTexCoord2f(rx2, self.z_base); glVertex3f(rx2, y_edge, self.z_base)
            glTexCoord2f(rx2, z_top); glVertex3f(rx2, y_edge, z_top)
            glTexCoord2f(rx1, z_top); glVertex3f(rx1, y_edge, z_top)
            glEnd()

        # Торцы правого леса
        rx, ry = self.right_points[0]
        glNormal3f(1, 0, 0)
        glBegin(GL_QUADS)
        glTexCoord2f(ry, self.z_base); glVertex3f(rx, ry, self.z_base)
        glTexCoord2f(y_edge, self.z_base); glVertex3f(rx, y_edge, self.z_base)
        glTexCoord2f(y_edge, z_top); glVertex3f(rx, y_edge, z_top)
        glTexCoord2f(ry, z_top); glVertex3f(rx, ry, z_top)
        glEnd()

        rx, ry = self.right_points[-1]
        glNormal3f(-1, 0, 0)
        glBegin(GL_QUADS)
        glTexCoord2f(ry, self.z_base); glVertex3f(rx, ry, self.z_base)
        glTexCoord2f(y_edge, self.z_base); glVertex3f(rx, y_edge, self.z_base)
        glTexCoord2f(y_edge, z_top); glVertex3f(rx, y_edge, z_top)
        glTexCoord2f(ry, z_top); glVertex3f(rx, ry, z_top)
        glEnd()

        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)

        glDisable(GL_TEXTURE_2D)

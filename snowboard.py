import math
from OpenGL.GL import *

class Snowboard:
    def __init__(self):
        self.length = 2.0
        self.width = 0.5
        self.thickness = 0.1
        self.scale = 2.0

        self.bottom = [
            (-1.1, -0.25),
            (-0.9, -0.25),
            (0.9, -0.25),
            (1.1, 0.0),
            (0.9, 0.0),
            (0.9, 0.25),
            (-0.9, 0.25),
            (-1.1, 0.25),
            (-0.9, 0.0),
        ]

        self.snowboarder = [
            (-0.25, -0.25),
            (0.25, 0),
            (-0.25, 0.25),
        ]

        self.world_x = 260.0
        self.world_y = 350.0
        self.world_z = 250.0
        self.angle = 0.0

        self.start_x = 260.0
        self.speed_kmh = 40.0
        self.speed_ms = self.speed_kmh * 1000.0 / 3600.0  # 11.11 м/с

        # Физика
        self.vx = 0.0
        self.vy = 0.0
        self.turn_input = 0.0
        self.turn_rate = 40

        self._phase = 0.0

        self.moving = False

    def start(self, center_line):
        # Идём по линии, пока не наберём 10 метров
        self.center_line = center_line
        remaining = 10.0
        for i in range(len(center_line) - 1):
            x1, y1 = center_line[i]
            x2, y2 = center_line[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            seg_len = (dx*dx + dy*dy) ** 0.5

            if remaining <= seg_len:
                frac = remaining / seg_len
                self.world_x = x1 + dx * frac
                self.world_y = y1 + dy * frac
                self.angle = math.degrees(math.atan2(dy, dx))
                break
            remaining -= seg_len

        self.vx = math.cos(math.radians(self.angle)) * self.speed_ms
        self.vy = math.sin(math.radians(self.angle)) * self.speed_ms
        self.moving = True
        self._generate_trajectory(center_line)

    def _generate_trajectory(self, center_line):
        self.trajectory_points = []
        self.bisector_lines = []
        self.wave_points = []

        cl_length = 0
        len_total = 0
        left = True
        wave_length = 20
        wave_half_amplitude = 5
        
        for i in range(len(center_line) - 1):
            x1, y1 = center_line[i]
            x2, y2 = center_line[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            seg_len = (dx*dx + dy*dy) ** 0.5
            cl_length += seg_len
            
            while len_total < cl_length:
                dist_in_seg = len_total - (cl_length - seg_len)
                if left:
                    self.wave_points.append((wave_half_amplitude, dist_in_seg, i))
                else:
                    self.wave_points.append((-wave_half_amplitude, dist_in_seg, i))
                len_total += wave_length
                left = not left

        for wave in self.wave_points:
            offset_y, dist_in_seg, seg_idx = wave
            x1, y1 = center_line[seg_idx]
            x2, y2 = center_line[seg_idx + 1]

            dx = x2 - x1
            dy = y2 - y1
            seg_len = (dx*dx + dy*dy) ** 0.5
            if seg_len == 0:
                continue

            # Направление сегмента (ось X)
            angle = math.atan2(dy, dx)
            forward_x = math.cos(angle)
            forward_y = math.sin(angle)

            # Перпендикуляр влево (ось Y)
            left_x = -math.sin(angle)
            left_y = math.cos(angle)

            # Точка на линии сегмента
            t = dist_in_seg / seg_len
            px = x1 + dx * t
            py = y1 + dy * t

            # Смещение перпендикулярно
            px += left_x * offset_y
            py += left_y * offset_y

            # Добавляем жёлтую точку
            self.trajectory_points.append((px, py, self.world_z + 0.05, 1.0, 1.0, 0.0))

    def update(self, dt, center_line=None):
        if not self.moving or not hasattr(self, 'trajectory_points') or not self.trajectory_points:
            return
    
        # Текущая скорость
        speed = self.speed_ms
    
        # Находим текущий сегмент траектории по перпендикуляру
        best_seg = 0
        best_t = 0.0
        best_dist = float('inf')
    
        for i in range(len(self.trajectory_points) - 1):
            x1, y1, _, _, _, _ = self.trajectory_points[i]
            x2, y2, _, _, _, _ = self.trajectory_points[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            seg_len_sq = dx*dx + dy*dy
            if seg_len_sq == 0:
                continue
    
            t = ((self.world_x - x1)*dx + (self.world_y - y1)*dy) / seg_len_sq
            t = max(0.0, min(1.0, t))
    
            px = x1 + dx * t
            py = y1 + dy * t
            dist = (self.world_x - px)**2 + (self.world_y - py)**2
    
            if dist < best_dist:
                best_dist = dist
                best_seg = i
                best_t = t
    
        # Если прошли больше половины — переключаемся на следующий сегмент
        if best_t > 0.5 and best_seg < len(self.trajectory_points) - 2:
            best_seg += 1
    
        # Целевая точка — конец текущего сегмента
        tx, ty, _, _, _, _ = self.trajectory_points[best_seg + 1]
    
        # Угол к цели
        target_angle = math.degrees(math.atan2(ty - self.world_y, tx - self.world_x))
    
        # Доворачиваем с угловой скоростью
        angle_diff = (target_angle - self.angle + 180) % 360 - 180
        max_turn = self.turn_rate * dt
        if angle_diff > max_turn:
            angle_diff = max_turn
        elif angle_diff < -max_turn:
            angle_diff = -max_turn
        self.angle += angle_diff
    
        # Двигаемся вперёд по направлению доски
        angle_rad = math.radians(self.angle)
        self.world_x += math.cos(angle_rad) * speed * dt
        self.world_y += math.sin(angle_rad) * speed * dt

    def draw(self):
        # Отрисовка центральной линии коридора

        if hasattr(self, 'bisector_lines') and self.bisector_lines:
            glDisable(GL_LIGHTING)
            glColor3f(0.0, 1.0, 0.0)
            glLineWidth(1.0)
            glBegin(GL_LINES)
            for bx1, by1, bx2, by2 in self.bisector_lines:
                glVertex3f(bx1, by1, self.world_z + 0.03)
                glVertex3f(bx2, by2, self.world_z + 0.03)
            glEnd()
            glEnable(GL_LIGHTING)

        if hasattr(self, 'center_line') and self.center_line:
            glDisable(GL_LIGHTING)
            glColor3f(1.0, 1.0, 0.0)  # жёлтый
            glLineWidth(1.0)
            glBegin(GL_LINE_STRIP)
            for x, y in self.center_line:
                glVertex3f(x, y, self.world_z + 0.05)
            glEnd()
            glEnable(GL_LIGHTING)

        # Отрисовка траектории
        if hasattr(self, 'trajectory_points') and self.trajectory_points:
            glDisable(GL_LIGHTING)
            glLineWidth(2.0)
            glBegin(GL_LINE_STRIP)
            for x, y, z, r, g, b in self.trajectory_points:
                glColor3f(r, g, b)
                glVertex3f(x, y, z)
            glEnd()
            glEnable(GL_LIGHTING)

        glPushMatrix()
        glTranslatef(self.world_x, self.world_y, self.world_z)
        glRotatef(self.angle, 0, 0, 1)
        glScalef(self.scale, self.scale, self.scale)

        glColor3f(0.1, 0.1, 0.1)
        z_bottom = 0.0
        z_top = self.thickness
        b = self.bottom

        # Нижний полигон
        glNormal3f(0, 0, -1)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(b[4][0], b[4][1], z_bottom)
        glVertex3f(b[8][0], b[8][1], z_bottom)
        glVertex3f(b[0][0], b[0][1], z_bottom)
        glVertex3f(b[1][0], b[1][1], z_bottom)
        glVertex3f(b[2][0], b[2][1], z_bottom)
        glVertex3f(b[3][0], b[3][1], z_bottom)
        glVertex3f(b[5][0], b[5][1], z_bottom)
        glVertex3f(b[6][0], b[6][1], z_bottom)
        glVertex3f(b[7][0], b[7][1], z_bottom)
        glVertex3f(b[8][0], b[8][1], z_bottom)
        glEnd()

        # Верхний полигон
        glNormal3f(0, 0, 1)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(b[4][0], b[4][1], z_top)
        glVertex3f(b[8][0], b[8][1], z_top)
        glVertex3f(b[0][0], b[0][1], z_top)
        glVertex3f(b[1][0], b[1][1], z_top)
        glVertex3f(b[2][0], b[2][1], z_top)
        glVertex3f(b[3][0], b[3][1], z_top)
        glVertex3f(b[5][0], b[5][1], z_top)
        glVertex3f(b[6][0], b[6][1], z_top)
        glVertex3f(b[7][0], b[7][1], z_top)
        glVertex3f(b[8][0], b[8][1], z_top)
        glEnd()

        # Канты
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 5),
            (5, 6), (6, 7), (7, 8), (8, 0),
        ]

        for i1, i2 in edges:
            x1, y1 = b[i1]
            x2, y2 = b[i2]
            dx = x2 - x1
            dy = y2 - y1
            nx = dy
            ny = -dx
            n_len = (nx*nx + ny*ny) ** 0.5
            if n_len > 0:
                nx /= n_len
                ny /= n_len
            glNormal3f(nx, ny, 0)
            glBegin(GL_QUADS)
            glVertex3f(x1, y1, z_bottom)
            glVertex3f(x2, y2, z_bottom)
            glVertex3f(x2, y2, z_top)
            glVertex3f(x1, y1, z_top)
            glEnd()

        # Сноубордист
        glColor3f(0.8, 0.1, 0.1)
        s = self.snowboarder
        z_b = self.thickness
        z_t = self.thickness + 2.0

        v1x = s[1][0] - s[0][0]
        v1y = s[1][1] - s[0][1]
        v2x = s[2][0] - s[0][0]
        v2y = s[2][1] - s[0][1]
        nx = v1y * 0 - 0 * v2y
        ny = 0 * v2x - v1x * 0
        nz = v1x * v2y - v1y * v2x
        n_len = (nx*nx + ny*ny + nz*nz) ** 0.5
        glNormal3f(nx/n_len, ny/n_len, nz/n_len)

        glBegin(GL_TRIANGLES)
        glVertex3f(s[0][0], s[0][1], z_t)
        glVertex3f(s[1][0], s[1][1], z_t)
        glVertex3f(s[2][0], s[2][1], z_t)
        glEnd()

        glNormal3f(-nx/n_len, -ny/n_len, -nz/n_len)
        glBegin(GL_TRIANGLES)
        glVertex3f(s[0][0], s[0][1], z_b)
        glVertex3f(s[1][0], s[1][1], z_b)
        glVertex3f(s[2][0], s[2][1], z_b)
        glEnd()

        side_edges = [(0, 1), (1, 2), (2, 0)]
        for i1, i2 in side_edges:
            x1, y1 = s[i1]
            x2, y2 = s[i2]
            dx = x2 - x1
            dy = y2 - y1
            nx = dy
            ny = -dx
            n_len = (nx*nx + ny*ny) ** 0.5
            glNormal3f(nx/n_len, ny/n_len, 0)
            glBegin(GL_QUADS)
            glVertex3f(x1, y1, z_b)
            glVertex3f(x2, y2, z_b)
            glVertex3f(x2, y2, z_t)
            glVertex3f(x1, y1, z_t)
            glEnd()

        glPopMatrix()
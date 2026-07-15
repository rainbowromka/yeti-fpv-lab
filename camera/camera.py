from OpenGL.GL import *
from OpenGL.GLU import *
from .stick import Stick
from .pid import PID
import math

class Camera:
    def __init__(self):
        self.pos_x = 255.5
        self.pos_y = 350.0
        # self.pos_z = 250.05
        self.pos_z = 270.05
        # self.pos_z = 251.5

        # self.forward_x = 1.0
        # self.forward_y = 0.0
        # self.forward_z = 0.0

        # self.up_x = 0.0
        # self.up_y = 0.0
        # self.up_z = 1.0
        self.forward_x = 0.919
        self.forward_y = 0.0
        self.forward_z = -0.395

        self.up_x = 0.395
        self.up_y = 0.0
        self.up_z = 0.919

        self.camera_angle = 25.0  # градусов

        self.move_speed = 100.0
        self.rotate_speed = 1.0

        self.throttle = Stick(1.0 / 0.5, 0.0, 1.0)
        self.throttle_direction = 0
        self.throttle_stick_speed = 1.0 / 1.5
        self.throttle.value = 0.356
        self.throttle.target = 0.356

        self.max_throttle_trust = 30

        self.vertical_speed = 0
        self.gravity = -9.81  # м/с²
        self.min_z = 250.05  # минимальная высота

        self.yaw = Stick(1 / 1.5, -1, 1, 0)
        self.yaw_direction = 0

        self.pitch = Stick(1.0 / 1.5, -1.0, 1.0, 0.0)
        self.pitch_direction = 0

        self.roll = Stick(1.0 / 1.5, -1.0, 1.0, 0.0)
        self.roll_direction = 0

        self.max_turn_speed = 120.0  # градусов/сек

        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0

        self.autopilot = False
        self.autopilot_target_x = 0.0
        self.autopilot_target_y = 0.0
        self.autopilot_target_z = 0.0

        self.pid_yaw = PID(kp=2.0 - 0.1 * 4, ki=0.1, kd=4.0, max_output=1.0)
        self.pid_roll = PID(kp=0.3, ki=0.0, kd=0.5, max_output=1.0)

        self.pid_distance = PID(kp=0.05, ki=0.01, kd=0.0, min_output=-1.0, max_output=1.0)
        self.pid_throttle = PID(kp=0.25, ki=0.0003, kd=0.233, min_output=-1.0, max_output=1.0)

        self.hover_throttle = 0.327  # начальная оценка газа висения
        self.throttle_correction = 0.0
        self._hover_integral = 0.0

        self.autopilot_start_time = 0.0
        self.autopilot_time = 0.0
        self.autopilot_target_reached = False
        self.height_error = 0.04

        self.target_pitch =0
        self.target_roll = 0
        self.distance_cmd = 0

    def toggle_autopilot(self, snowboard):
        self.autopilot = not self.autopilot
        if self.autopilot:
            self.autopilot_start_time = 0.0  # обнулим при старте
            self.autopilot_time = 0.0
            self.autopilot_target_reached = True
            self.pid_yaw.reset()
            self.pid_roll.reset()
            self.pid_throttle.reset()
        else:
            self.autopilot_time = 0.0
            self.autopilot_target_reached = False

    def apply(self):
        # Поворачиваем forward на camera_angle вверх
        angle = math.radians(self.camera_angle)

        # right = forward × up
        rx = self.forward_y * self.up_z - self.forward_z * self.up_y
        ry = self.forward_z * self.up_x - self.forward_x * self.up_z
        rz = self.forward_x * self.up_y - self.forward_y * self.up_x
        
        r_len = math.sqrt(rx*rx + ry*ry + rz*rz)
        if r_len > 0:
            rx /= r_len
            ry /= r_len
            rz /= r_len
        
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # forward камеры = forward * cos + up * sin
        cam_fx = self.forward_x * cos_a + self.up_x * sin_a
        cam_fy = self.forward_y * cos_a + self.up_y * sin_a
        cam_fz = self.forward_z * cos_a + self.up_z * sin_a
        
        # up камеры = -forward * sin + up * cos
        cam_ux = -self.forward_x * sin_a + self.up_x * cos_a
        cam_uy = -self.forward_y * sin_a + self.up_y * cos_a
        cam_uz = -self.forward_z * sin_a + self.up_z * cos_a
        
        target_x = self.pos_x + cam_fx * 1000
        target_y = self.pos_y + cam_fy * 1000
        target_z = self.pos_z + cam_fz * 1000
        
        glLoadIdentity()
        gluLookAt(
            self.pos_x, self.pos_y, self.pos_z,
            target_x, target_y, target_z,
            cam_ux, cam_uy, cam_uz
        )

    def _get_direction(self):
        dx = self.forward_x
        dy = self.forward_y
        dz = self.forward_z
        return (dx, dy, dz)

    def update(self, dt, snowboard=None):
        if self.autopilot and snowboard is not None:
            self.throttle_direction = 0
            self.yaw_direction = 0
            self.pitch_direction = 0
            self.roll_direction = 0
            self._autopilot_update(dt, snowboard)

        if self.throttle_direction != 0:
            self.throttle.set_target(self.throttle_direction * dt * self.throttle_stick_speed)
        self.throttle_direction = 0

        self.throttle.update(dt)

        # Вектор тяги (по up)
        thrust_x = self.up_x * self.throttle.value * self.max_throttle_trust
        thrust_y = self.up_y * self.throttle.value * self.max_throttle_trust
        thrust_z = self.up_z * self.throttle.value * self.max_throttle_trust
    
        # Вектор гравитации (по Z вниз)
        grav_x = 0.0
        grav_y = 0.0
        grav_z = self.gravity  # -9.81
    
        # Итоговое ускорение
        accel_x = thrust_x + grav_x
        accel_y = thrust_y + grav_y
        accel_z = thrust_z + grav_z
    
        # Интегрируем скорость
        self.vx += accel_x * dt
        self.vy += accel_y * dt
        self.vz += accel_z * dt
    
        # Сопротивление воздуха
        self.vx *= 0.99
        self.vy *= 0.99
        self.vz *= 0.99
    
        # Обновляем позицию
        self.pos_x += self.vx * dt
        self.pos_y += self.vy * dt
        self.pos_z += self.vz * dt
    
        # Не ниже min_z
        if self.pos_z <= self.min_z:
            self.pos_z = self.min_z
            self.vz = 0.0

        # Рыскание (yaw) — вокруг up
        # yaw_angle = self.yaw_gas * self.max_turn_speed * dt
        if self.yaw_direction != 0:
            self.yaw.set_target(self.yaw_direction * dt)
        self.yaw_direction = 0
        self.yaw.update(dt)

        yaw_angle = self.yaw.value * self.max_turn_speed * dt
        if yaw_angle != 0:
            angle = math.radians(yaw_angle)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
    
            # right = forward × up
            rx = self.forward_y * self.up_z - self.forward_z * self.up_y
            ry = self.forward_z * self.up_x - self.forward_x * self.up_z
            rz = self.forward_x * self.up_y - self.forward_y * self.up_x
            r_len = math.sqrt(rx*rx + ry*ry + rz*rz)
            if r_len > 0:
                rx /= r_len
                ry /= r_len
                rz /= r_len
    
            fx = self.forward_x * cos_a + rx * sin_a
            fy = self.forward_y * cos_a + ry * sin_a
            fz = self.forward_z * cos_a + rz * sin_a
    
            f_len = math.sqrt(fx*fx + fy*fy + fz*fz)
            self.forward_x = fx / f_len
            self.forward_y = fy / f_len
            self.forward_z = fz / f_len
    
        # Тангаж (pitch) — вокруг right
        if self.pitch_direction != 0:
            self.pitch.set_target(self.pitch_direction * dt)
        self.pitch_direction = 0
        self.pitch.update(dt)

        pitch_angle = self.pitch.value * self.max_turn_speed * dt

        if pitch_angle != 0:
            angle = math.radians(pitch_angle)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
    
            # right = forward × up
            rx = self.forward_y * self.up_z - self.forward_z * self.up_y
            ry = self.forward_z * self.up_x - self.forward_x * self.up_z
            rz = self.forward_x * self.up_y - self.forward_y * self.up_x
            r_len = math.sqrt(rx*rx + ry*ry + rz*rz)
            if r_len > 0:
                rx /= r_len
                ry /= r_len
                rz /= r_len
    
            fx = self.forward_x * cos_a + self.up_x * sin_a
            fy = self.forward_y * cos_a + self.up_y * sin_a
            fz = self.forward_z * cos_a + self.up_z * sin_a
    
            ux = -self.forward_x * sin_a + self.up_x * cos_a
            uy = -self.forward_y * sin_a + self.up_y * cos_a
            uz = -self.forward_z * sin_a + self.up_z * cos_a
    
            f_len = math.sqrt(fx*fx + fy*fy + fz*fz)
            self.forward_x = fx / f_len
            self.forward_y = fy / f_len
            self.forward_z = fz / f_len
    
            u_len = math.sqrt(ux*ux + uy*uy + uz*uz)
            self.up_x = ux / u_len
            self.up_y = uy / u_len
            self.up_z = uz / u_len

        # Крен (roll) — вокруг forward

        if self.roll_direction != 0:
            self.roll.set_target(self.roll_direction * dt)
        self.roll_direction = 0
        self.roll.update(dt)

        roll_angle = self.roll.value * self.max_turn_speed * dt
        if roll_angle != 0:
            angle = math.radians(roll_angle)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)

            # right = forward × up
            rx = self.forward_y * self.up_z - self.forward_z * self.up_y
            ry = self.forward_z * self.up_x - self.forward_x * self.up_z
            rz = self.forward_x * self.up_y - self.forward_y * self.up_x
            r_len = math.sqrt(rx*rx + ry*ry + rz*rz)
            if r_len > 0:
                rx /= r_len
                ry /= r_len
                rz /= r_len

            ux = self.up_x * cos_a + rx * sin_a
            uy = self.up_y * cos_a + ry * sin_a
            uz = self.up_z * cos_a + rz * sin_a

            u_len = math.sqrt(ux*ux + uy*uy + uz*uz)
            self.up_x = ux / u_len
            self.up_y = uy / u_len
            self.up_z = uz / u_len


    def _autopilot_update(self, dt, snowboard):
        sb_angle = math.radians(snowboard.angle)
        sb_fx = math.cos(sb_angle)
        sb_fy = math.sin(sb_angle)

        target_x = snowboard.world_x - sb_fx * 20.0
        target_y = snowboard.world_y - sb_fy * 20.0
        target_z = snowboard.world_z + 1.5

        # Вектор от дрона к сноубордисту
        to_sb_x = snowboard.world_x - self.pos_x
        to_sb_y = snowboard.world_y - self.pos_y
        to_sb_z = snowboard.world_z - self.pos_z

        # right = forward × up
        right_x = self.forward_y * self.up_z - self.forward_z * self.up_y
        right_y = self.forward_z * self.up_x - self.forward_x * self.up_z
        right_z = self.forward_x * self.up_y - self.forward_y * self.up_x
        r_len = math.sqrt(right_x**2 + right_y**2 + right_z**2)
        if r_len > 0:
            right_x /= r_len
            right_y /= r_len
            right_z /= r_len

        # Проекция на forward
        proj_forward = to_sb_x*self.forward_x + to_sb_y*self.forward_y + to_sb_z*self.forward_z
        # Проекция на right
        proj_right = to_sb_x*right_x + to_sb_y*right_y + to_sb_z*right_z

        # Yaw: угол между forward и направлением на цель в плоскости дрона
        angle_diff = math.atan2(proj_right, proj_forward)
        yaw_cmd = self.pid_yaw.update(angle_diff, dt)
        self.yaw.set_target(yaw_cmd * dt * 2.0)

        # Roll: выравнивание горизонта
        # roll_angle = math.atan2(right_z, math.sqrt(right_x**2 + right_y**2))
        # roll_cmd = self.pid_roll.update(roll_angle, dt)
        # self.roll.set_target(roll_cmd * dt * 2.0)

        self._follow_to_snowboarder(dt, snowboard)
        self._autopilot_throttle(dt, target_z)

    def move_toward_target(self, dt):
        self.pos_x += self.forward_x * dt
        self.pos_y += self.forward_y * dt
        self.pos_z += self.forward_z * dt

    def pitch(self, dt):
        angle = math.radians(self.rotate_speed * dt)

        rx = self.forward_y * self.up_z - self.forward_z * self.up_y
        ry = self.forward_z * self.up_x - self.forward_x * self.up_z
        rz = self.forward_x * self.up_y - self.forward_y * self.up_x

        r_len = math.sqrt(rx*rx + ry*ry + rz*rz)
        rx /= r_len
        ry /= r_len
        rz /= r_len

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        fx = self.forward_x * cos_a + self.up_x * sin_a
        fy = self.forward_y * cos_a + self.up_y * sin_a
        fz = self.forward_z * cos_a + self.up_z * sin_a

        ux = -self.forward_x * sin_a + self.up_x * cos_a
        uy = -self.forward_y * sin_a + self.up_y * cos_a
        uz = -self.forward_z * sin_a + self.up_z * cos_a

        self.forward_x = fx
        self.forward_y = fy
        self.forward_z = fz
        self.up_x = ux
        self.up_y = uy
        self.up_z = uz

        f_len = math.sqrt(fx*fx + fy*fy + fz*fz)
        self.forward_x /= f_len
        self.forward_y /= f_len
        self.forward_z /= f_len

        u_len = math.sqrt(ux*ux + uy*uy + uz*uz)
        self.up_x /= u_len
        self.up_y /= u_len
        self.up_z /= u_len

    def rotate_left(self, dt):
        angle = math.radians(self.rotate_speed * dt)

        rx = self.forward_y * self.up_z - self.forward_z * self.up_y
        ry = self.forward_z * self.up_x - self.forward_x * self.up_z
        rz = self.forward_x * self.up_y - self.forward_y * self.up_x

        r_len = math.sqrt(rx*rx + ry*ry + rz*rz)
        rx /= r_len
        ry /= r_len
        rz /= r_len

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        self.forward_x = self.forward_x * cos_a + rx * sin_a
        self.forward_y = self.forward_y * cos_a + ry * sin_a
        self.forward_z = self.forward_z * cos_a + rz * sin_a

        f_len = math.sqrt(self.forward_x**2 + self.forward_y**2 + self.forward_z**2)
        self.forward_x /= f_len
        self.forward_y /= f_len
        self.forward_z /= f_len

    def strafe(self, dt):
        rx = self.forward_y * self.up_z - self.forward_z * self.up_y
        ry = self.forward_z * self.up_x - self.forward_x * self.up_z
        rz = self.forward_x * self.up_y - self.forward_y * self.up_x

        r_len = math.sqrt(rx*rx + ry*ry + rz*rz)
        rx /= r_len
        ry /= r_len
        rz /= r_len

        speed = self.move_speed * dt

        self.pos_x += rx * speed
        self.pos_y += ry * speed
        self.pos_z += rz * speed

    def get_info(self):
        return {
            'position': (round(self.pos_x, 1),
                         round(self.pos_y, 1),
                         round(self.pos_z, 1)),
            'throttle': round(self.throttle.value * 100, 0),
            'throttle_target': round(self.throttle.target * 100, 0),
            'yaw': round(self.yaw.value * 100, 0),
            'yaw_target': round(self.yaw.target * 100, 0),
            'roll': round(self.roll.value * 100, 0),
            'roll_target': round(self.roll.target * 100, 0),
            'elevation': round(self.pos_z, 1),
            'throttle_correction': round (self.throttle_correction, 1),
            'autopilot_time': round(self.autopilot_time, 2),
            'autopilot_target_reached': self.autopilot_target_reached,
            'target_pitch': round(self.target_pitch, 2) if hasattr(self, 'target_pitch') else 0,
            'target_roll': round(self.target_roll, 2) if hasattr(self, 'target_roll') else 0,
            'distance_cmd': round(self.distance_cmd, 2) if hasattr(self, 'distance_cmd') else 0,
        }

    def get_vectors_info(self):
        f_len = math.sqrt(self.forward_x**2 + self.forward_y**2 + self.forward_z**2)
        u_len = math.sqrt(self.up_x**2 + self.up_y**2 + self.up_z**2)

        dot = self.forward_x*self.up_x + self.forward_y*self.up_y + self.forward_z*self.up_z

        return {
            'forward': (round(self.forward_x, 3), round(self.forward_y, 3), round(self.forward_z, 3)),
            'forward_len': round(f_len, 6),
            'up': (round(self.up_x, 3), round(self.up_y, 3), round(self.up_z, 3)),
            'up_len': round(u_len, 6),
            'dot': round(dot, 6)
        }

    def _autopilot_throttle(self, dt, target_z):
        height_error = target_z - self.pos_z

        if self.up_z > 0.001:
            self.hover_throttle = abs(self.gravity) / (self.up_z * self.max_throttle_trust)
        else:
            self.hover_throttle = 0

        # ПИД выдаёт от -1 до 1
        raw_throttle = self.pid_throttle.update(height_error, dt)

        if raw_throttle < 0:
            # Пропорционально от 0 до hover_throttle
            target_throttle = self.hover_throttle + raw_throttle * self.hover_throttle
        elif raw_throttle == 0:
            target_throttle = self.hover_throttle
        else:  # raw_throttle > 0
            # Пропорционально от hover_throttle до 1
            target_throttle = self.hover_throttle + raw_throttle * (1.0 - self.hover_throttle)

        self.throttle.target = target_throttle


    def _follow_to_snowboarder(self, dt, snowboard):
        sb_angle = math.radians(snowboard.angle)
        sb_fx = math.cos(sb_angle)
        sb_fy = math.sin(sb_angle)

        target_x = snowboard.world_x - sb_fx * 20.0
        target_y = snowboard.world_y - sb_fy * 20.0
        target_z = snowboard.world_z + 1.5

        self.autopilot_target_x = target_x
        self.autopilot_target_y = target_y
        self.autopilot_target_z = target_z

        # Вектор от дрона к цели
        to_x = target_x - self.pos_x
        to_y = target_y - self.pos_y
        to_z = target_z - self.pos_z
        dist = math.sqrt(to_x**2 + to_y**2 + to_z**2)
        if dist > 0.01:
            to_x /= dist
            to_y /= dist
            to_z /= dist

        # Мировая вертикаль
        world_up_x = 0.0
        world_up_y = 0.0
        world_up_z = 1.0

        # Плоскость: pos, pos + target, pos + world_up
        # Нормаль к плоскости
        nx = to_y * world_up_z - to_z * world_up_y  # = to_y * 1
        ny = to_z * world_up_x - to_x * world_up_z  # = -to_x
        nz = to_x * world_up_y - to_y * world_up_x  # = 0
        n_len = math.sqrt(nx*nx + ny*ny + nz*nz)
        if n_len > 0:
            nx /= n_len
            ny /= n_len
            nz /= n_len

        # Желаемый up: повёрнут на 45° от мировой вертикали к цели в этой плоскости
        max_angle = math.radians(45)
        cos_a = math.cos(max_angle)
        sin_a = math.sin(max_angle)

        # Вращаем world_up вокруг нормали n на 45° к цели
        # Формула Родригеса
        dot = world_up_x*nx + world_up_y*ny + world_up_z*nz
        target_up_x = nx*dot*(1-cos_a) + world_up_x*cos_a + (ny*world_up_z - nz*world_up_y)*sin_a
        target_up_y = ny*dot*(1-cos_a) + world_up_y*cos_a + (nz*world_up_x - nx*world_up_z)*sin_a
        target_up_z = nz*dot*(1-cos_a) + world_up_z*cos_a + (nx*world_up_y - ny*world_up_x)*sin_a

        # right дрона
        right_x = self.forward_y * self.up_z - self.forward_z * self.up_y
        right_y = self.forward_z * self.up_x - self.forward_x * self.up_z
        right_z = self.forward_x * self.up_y - self.forward_y * self.up_x
        r_len = math.sqrt(right_x**2 + right_y**2 + right_z**2)
        if r_len > 0:
            right_x /= r_len
            right_y /= r_len
            right_z /= r_len

        # Проекция target_up на плоскости дрона
        proj_right = target_up_x*right_x + target_up_y*right_y + target_up_z*right_z
        proj_forward = target_up_x*self.forward_x + target_up_y*self.forward_y + target_up_z*self.forward_z
        proj_up = target_up_x*self.up_x + target_up_y*self.up_y + target_up_z*self.up_z

        # Углы поворота, чтобы довернуть текущий up до target_up:
        # pitch = угол в плоскости forward-up
        # roll = угол в плоскости right-up
        self.target_pitch = math.atan2(proj_forward, proj_up)
        self.target_roll = math.atan2(proj_right, proj_up)

        self.distance_cmd = self.pid_distance.update(dist, dt)  # -1..1
        #
        self.target_pitch = self.target_pitch * self.distance_cmd
        # self.target_roll = self.target_roll * distance_cmd
        #
        self.target_pitch = max(-max_angle, min(max_angle, self.target_pitch))
        # self.target_roll = max(-max_angle, min(max_angle, self.target_roll))

        # Итоговые углы

        # Задаём стикам: target = final_angle / max_angle (приведение к -1..1)
        self.pitch.target = self.target_pitch / max_angle
        # self.roll.target = self.target_roll / max_angle
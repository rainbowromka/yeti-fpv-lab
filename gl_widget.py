from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import QTimer, Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from camera import Camera
from scene import Scene
import time

class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.camera = Camera()
        self.scene = Scene()

        self.keys = set()
        self.last_time = time.time()

        self.setFocusPolicy(Qt.StrongFocus)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def initializeGL(self):
        glEnable(GL_MULTISAMPLE)
        # glClearColor(0.1, 0.1, 0.1, 1.0)
        glClearColor(0.4, 0.6, 0.9, 1.0)  # голубой (небо)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        # Направленный свет слева направо
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 0.0, -0.5, 0.0])  # w=0 = направленный
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h, 1.0, 10000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
    
        self.camera.update(dt, self.scene.snowboard)
        self.scene.update(dt)
        self._handle_keys()
        self.camera.apply()
    
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 0.0, -0.5, 0.0])
    
        self.scene.draw()


    def _handle_keys(self):
        if Qt.Key_W in self.keys:
            self.camera.throttle_direction = 1
        if Qt.Key_S in self.keys:
            self.camera.throttle_direction = -1
        if Qt.Key_I in self.keys:
            self.camera.pitch_direction = -1
        if Qt.Key_K in self.keys:
            self.camera.pitch_direction = 1
        if Qt.Key_A in self.keys:
            self.camera.yaw_direction = -1
        if Qt.Key_D in self.keys:
            self.camera.yaw_direction = 1
        if Qt.Key_J in self.keys:
            self.camera.roll_direction = - 1
        if Qt.Key_L in self.keys:
            self.camera.roll_direction = 1
        if Qt.Key_Q in self.keys:
            self.camera.throttle.reset()
            self.camera.yaw.reset()
            self.camera.pitch.reset()
            self.camera.roll.reset()
        if Qt.Key_O in self.keys:
            self.camera.yaw.reset()
            self.camera.pitch.reset()
            self.camera.roll.reset()

    def keyPressEvent(self, event):
        self.keys.add(event.key())
        if event.key() == Qt.Key_Space:
            # Пауза/продолжить
            self.scene.snowboard.moving = not self.scene.snowboard.moving
        elif event.key() == Qt.Key_R:
            # Перезапуск сноубордиста
            self.scene.snowboard.start(self.scene.corridor.center_line)
        elif event.key() == Qt.Key_T:
            # Новая трасса
            self.scene.regenerate()
        elif event.key() == Qt.Key_F:
            self.camera.toggle_autopilot(self.scene.snowboard)

    def keyReleaseEvent(self, event):
        self.keys.discard(event.key())

    def get_camera_info(self):
        info = self.camera.get_info()
        info['snowboard_z'] = round(self.scene.snowboard.world_z + 1.5, 1)
        vec = self.camera.get_vectors_info()
        info.update(vec)
        return info

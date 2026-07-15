import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QSurfaceFormat
from gl_widget import GLWidget
from info_panel import InfoPanel

# Включаем MSAA 4x
fmt = QSurfaceFormat()
fmt.setSamples(4)
QSurfaceFormat.setDefaultFormat(fmt)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Scene Analyzer")
        self.resize(800, 480)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #323236; }
            QWidget { background-color: #323236; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        left_container = QWidget()
        left_container.setFixedWidth(400)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.gl_widget = GLWidget()
        self.gl_widget.setFixedSize(320, 240)
        self.gl_widget.setStyleSheet("border: 2px solid #646464;")
        
        left_layout.addStretch()
        left_layout.addWidget(self.gl_widget, alignment=Qt.AlignCenter)
        left_layout.addStretch()
        
        self.info_panel = InfoPanel()
        
        layout.addWidget(left_container)
        layout.addWidget(self.info_panel)
        
        # Таймер для обновления инфо о камере
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_info)
        self.update_timer.start(100)  # 10 раз в секунду
    
    def _update_info(self):
        """Обновляет информацию о камере в правой панели"""
        cam_info = self.gl_widget.get_camera_info()
        self.info_panel.update_camera_info(cam_info)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
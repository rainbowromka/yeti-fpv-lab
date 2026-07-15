from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class InfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("3D Scene Analyzer")
        title.setStyleSheet("color: #FFC800; font-size: 18px; font-weight: bold; background: transparent;")
        layout.addWidget(title)

        info = QLabel(
            "Planes (1000x1000m):\n"
            "  RED - XY (Z=0) back wall\n"
            "  GREEN - XZ (Y=0) floor\n"
            "  BLUE - YZ (X=0) left wall\n"
            "\n"
            "Controls:\n"
            "  W/S - forward/back\n"
            "  A/D - left/right\n"
            "  I/K - up/down"
        )
        info.setStyleSheet("color: #DCDCDC; font-size: 13px; background: transparent;")
        layout.addWidget(info)

        self.camera_label = QLabel("Camera: waiting...")
        self.camera_label.setStyleSheet("color: #FFC800; font-size: 14px; background: transparent;")
        layout.addWidget(self.camera_label)

        layout.addStretch()

    def update_camera_info(self, info):
        text = (
            f"Throttle: {info['throttle']}%    Target: {info['throttle_target']}%\n"
            f"Yaw: {info['yaw']}%    Target: {info['yaw_target']}%\n"
            f"Roll: {info['roll']}%    Target: {info['roll_target']}%\n"
            f"Snowboard Z: {info.get('snowboard_z', 'N/A')}    Elevation: {info.get('elevation', 'N/A')}\n"
            f"Throttle Correction: {info.get('throttle_correction', 'N/A')}%\n"
            f"Forward: ({info['forward'][0]}, {info['forward'][1]}, {info['forward'][2]})\n"
            f"Up: ({info['up'][0]}, {info['up'][1]}, {info['up'][2]})\n"
            f"Autopilot Time: {info.get('autopilot_time', 0)}s\n"
            f"Pitch: {info.get('target_pitch', 0)}    Roll: {info.get('target_roll', 0)}\n"
            f"distance_cmd: {info.get('distance_cmd', 0)}"
        )
        self.camera_label.setText(text)

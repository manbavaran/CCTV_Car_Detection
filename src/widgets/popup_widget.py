from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt


class PopupPreviewWidget(QWidget):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config

        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.message_label = QLabel()
        self.message_label.setFont(QFont("Arial", 10))

        self.title_label.setAlignment(Qt.AlignCenter)
        self.message_label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
        self.setLayout(layout)

        self.update_preview()

    def update_config(self, config: dict):
        self.config = config
        self.update_preview()

    def update_preview(self):
        title = self.config.get("title", "차량 감지 알림!")
        message = self.config.get("message", "차량이 감지되었습니다.")
        width = self.config.get("width", 300)
        height = self.config.get("height", 100)
        bg_color = self.config.get("bg_color", "#ffffcc")

        self.title_label.setText(title)
        self.message_label.setText(message)

        self.setFixedSize(width, height)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(bg_color))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

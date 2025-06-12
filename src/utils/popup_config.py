import os
import json
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
import pyttsx3

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/alert_popup_config.json"))

def load_popup_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "title": "차량 감지 알림!",
        "message": "차량이 감지되었습니다.",
        "width": 300,
        "height": 100,
        "bg_color": "#ffffcc",
        "enabled": True,
        "tts": False
    }

def save_popup_config(config: dict):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

class PopupPreviewWidget(QWidget):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Widget)

        self.label_title = QLabel()
        self.label_message = QLabel()
        self.label_title.setStyleSheet("font-weight: bold; font-size: 14pt")
        self.label_message.setStyleSheet("font-size: 10pt")

        self.tts_button = QPushButton("🔊 미리 듣기")
        self.tts_button.clicked.connect(self.play_tts)

        layout = QVBoxLayout()
        layout.addWidget(self.label_title)
        layout.addWidget(self.label_message)
        layout.addWidget(self.tts_button)
        self.setLayout(layout)

        self.tts_engine = pyttsx3.init()
        self.config = config
        self.update_preview(config)

    def update_preview(self, config: dict):
        self.config = config
        self.setFixedSize(config.get("width", 300), config.get("height", 100))
        self.label_title.setText(config.get("title", "차량 감지 알림!"))
        self.label_message.setText(config.get("message", "차량이 감지되었습니다."))

        color = QColor(config.get("bg_color", "#ffffcc"))
        palette = self.palette()
        palette.setColor(QPalette.Window, color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def play_tts(self):
        if self.config.get("tts", False):
            text = self.config.get("message", "차량이 감지되었습니다.")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()

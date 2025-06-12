import os
import json
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QSpinBox, QColorDialog, QColor, QCheckBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from utils.popup_config import PopupPreviewWidget, load_popup_config, save_popup_config


class PopupAdvancedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("알림창 고급 설정")
        self.setGeometry(400, 400, 420, 400)

        self.config = load_popup_config()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 알림창 사용 여부 체크박스
        self.enable_check = QCheckBox("알림창 사용")
        self.enable_check.setChecked(self.config.get("enabled", True))
        self.layout.addWidget(self.enable_check)

        # 제목 입력
        self.title_input = QLineEdit(self.config.get("title", ""))
        self.layout.addWidget(QLabel("제목"))
        self.layout.addWidget(self.title_input)

        # 메시지 입력
        self.message_input = QLineEdit(self.config.get("message", ""))
        self.layout.addWidget(QLabel("내용"))
        self.layout.addWidget(self.message_input)

        # 너비/높이 설정
        self.width_input = QSpinBox()
        self.width_input.setRange(100, 1000)
        self.width_input.setValue(self.config.get("width", 300))

        self.height_input = QSpinBox()
        self.height_input.setRange(50, 800)
        self.height_input.setValue(self.config.get("height", 100))

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("너비"))
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(QLabel("높이"))
        size_layout.addWidget(self.height_input)
        self.layout.addLayout(size_layout)

        # 배경색 설정 버튼
        self.color_btn = QPushButton("배경색 선택")
        self.color_btn.clicked.connect(self.select_color)
        self.bg_color = self.config.get("bg_color", "#ffffcc")
        self.layout.addWidget(self.color_btn)

        # 미리보기 영역
        self.layout.addWidget(QLabel("미리보기"))
        self.preview = PopupPreviewWidget(self.config)
        self.layout.addWidget(self.preview)

        # 설정 적용 버튼
        self.save_btn = QPushButton("설정 저장")
        self.save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_btn)

        # 각 입력값 변경 시 프리뷰 업데이트 연결
        self.enable_check.stateChanged.connect(self.update_preview)
        self.title_input.textChanged.connect(self.update_preview)
        self.message_input.textChanged.connect(self.update_preview)
        self.width_input.valueChanged.connect(self.update_preview)
        self.height_input.valueChanged.connect(self.update_preview)

    def select_color(self):
        color = QColorDialog.getColor(QColor(self.bg_color), self, "배경색 선택")
        if color.isValid():
            self.bg_color = color.name()
            self.update_preview()

    def update_preview(self):
        config = {
            "enabled": self.enable_check.isChecked(),
            "title": self.title_input.text(),
            "message": self.message_input.text(),
            "width": self.width_input.value(),
            "height": self.height_input.value(),
            "bg_color": self.bg_color
        }
        self.preview.update_config(config)

    def save_settings(self):
        config = {
            "enabled": self.enable_check.isChecked(),
            "title": self.title_input.text(),
            "message": self.message_input.text(),
            "width": self.width_input.value(),
            "height": self.height_input.value(),
            "bg_color": self.bg_color
        }
        save_popup_config(config)
        self.accept()

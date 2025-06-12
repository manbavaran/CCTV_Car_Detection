from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QFileDialog, QMessageBox
)
import os
from utils.alert_utils import get_available_sounds, play_alert_sound

class SoundAdvancedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("소리 고급 설정")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("사용 가능한 알림음 목록:")
        layout.addWidget(self.label)

        self.sound_list = QListWidget()
        for sound in get_available_sounds():
            self.sound_list.addItem(sound)
        layout.addWidget(self.sound_list)

        btn_layout = QHBoxLayout()

        self.test_btn = QPushButton("선택한 소리 재생")
        self.test_btn.clicked.connect(self.play_selected_sound)
        btn_layout.addWidget(self.test_btn)

        self.add_btn = QPushButton("음원 추가")
        self.add_btn.clicked.connect(self.add_custom_sound)
        btn_layout.addWidget(self.add_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def play_selected_sound(self):
        selected = self.sound_list.currentItem()
        if selected:
            sound_name = selected.text()
            try:
                play_alert_sound(0.8, sound_name)
            except Exception as e:
                QMessageBox.warning(self, "재생 실패", str(e))

    def add_custom_sound(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "음원 선택", "", "MP3 Files (*.mp3)")
        if file_path:
            filename = os.path.basename(file_path)
            sounds_dir = os.path.join("resources", "sounds")
            os.makedirs(sounds_dir, exist_ok=True)
            dest_path = os.path.join(sounds_dir, filename)
            if not os.path.exists(dest_path):
                try:
                    import shutil
                    shutil.copy(file_path, dest_path)
                    self.sound_list.addItem(filename)
                except Exception as e:
                    QMessageBox.warning(self, "오류", f"파일 복사 실패: {e}")
            else:
                QMessageBox.information(self, "이미 존재", "이미 해당 파일이 존재합니다.")

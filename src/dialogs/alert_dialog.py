from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QFileDialog, QMessageBox
)
from utils.alert_utils import get_sound_list, play_alert_sound, add_custom_sound

class SoundAdvancedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("소리 고급 설정")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()
        self.label = QLabel("사용 가능한 알림음 목록:")
        layout.addWidget(self.label)

        self.sound_list = QListWidget()
        self.refresh_sound_list()
        layout.addWidget(self.sound_list)

        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("선택한 소리 재생")
        self.test_btn.clicked.connect(self.play_selected_sound)
        btn_layout.addWidget(self.test_btn)

        self.add_btn = QPushButton("음원 추가")
        self.add_btn.clicked.connect(self.add_custom_sound_file)
        btn_layout.addWidget(self.add_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def refresh_sound_list(self):
        self.sound_list.clear()
        for sound in get_sound_list():
            self.sound_list.addItem(sound)

    def play_selected_sound(self):
        selected = self.sound_list.currentItem()
        if selected:
            sound_name = selected.text()
            try:
                play_alert_sound(sound_name)
            except Exception as e:
                QMessageBox.warning(self, "재생 실패", str(e))

    def add_custom_sound_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "음원 선택", "", "MP3 Files (*.mp3 *.wav)")
        if file_path:
            try:
                filename = add_custom_sound(file_path)
                self.refresh_sound_list()
                QMessageBox.information(self, "성공", f"{filename} 파일이 추가되었습니다.")
            except Exception as e:
                QMessageBox.warning(self, "오류", f"파일 복사 실패: {e}")

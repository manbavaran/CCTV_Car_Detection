import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QPushButton, QLabel, QCheckBox,
    QHBoxLayout, QListWidget, QLineEdit, QGroupBox, QFormLayout, QSlider, QFileDialog
)
from PyQt5.QtCore import Qt

class ControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("차량 감지 시스템")
        self.setGeometry(100, 100, 600, 500)

        self.tabs = QTabWidget()

        self.tabs.addTab(self.profile_tab_ui(), "프로필")
        self.tabs.addTab(self.detection_tab_ui(), "감지")
        self.tabs.addTab(self.alert_tab_ui(), "알림 설정")
        self.tabs.addTab(self.system_tab_ui(), "시스템 설정")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def profile_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.profile_list = QListWidget()
        layout.addWidget(QLabel("프로필 목록"))
        layout.addWidget(self.profile_list)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("프로필 추가"))
        btn_layout.addWidget(QPushButton("프로필 삭제"))
        layout.addLayout(btn_layout)

        self.auto_profile_cb = QCheckBox("프로그램 시작 시 이 프로필 자동 선택")
        layout.addWidget(self.auto_profile_cb)

        layout.addWidget(QPushButton("ROI 설정 (점찍기)"))
        layout.addWidget(QLabel("점 크기 설정 (px)"))
        self.point_size_slider = QSlider(Qt.Horizontal)
        self.point_size_slider.setMinimum(1)
        self.point_size_slider.setMaximum(20)
        layout.addWidget(self.point_size_slider)

        layout.addWidget(QPushButton("고급 설정"))

        tab.setLayout(layout)
        return tab

    def detection_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.status_label = QLabel("감지 상태: 대기 중")
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("감지 시작"))
        btn_layout.addWidget(QPushButton("감지 종료"))
        layout.addLayout(btn_layout)

        self.auto_shutdown_cb = QCheckBox("감지 종료 후 프로그램 종료")
        layout.addWidget(self.auto_shutdown_cb)

        self.auto_start_cb = QCheckBox("프로그램 실행 시 감지 자동 시작")
        layout.addWidget(self.auto_start_cb)

        layout.addWidget(QPushButton("고급 설정"))

        tab.setLayout(layout)
        return tab

    def alert_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.use_sound_cb = QCheckBox("소리 알림 사용")
        layout.addWidget(self.use_sound_cb)
        layout.addWidget(QLabel("음량 설정"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        layout.addWidget(self.volume_slider)

        layout.addWidget(QLabel("지속시간 (초)"))
        self.duration_input = QLineEdit("3")
        layout.addWidget(self.duration_input)

        layout.addWidget(QPushButton("알림음 선택"))

        self.use_popup_cb = QCheckBox("팝업 알림 사용")
        layout.addWidget(self.use_popup_cb)
        layout.addWidget(QPushButton("고급 팝업 설정"))

        tab.setLayout(layout)
        return tab

    def system_tab_ui(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.obs_cb = QCheckBox("OBS 자동 실행")
        layout.addWidget(self.obs_cb)
        layout.addWidget(QPushButton("설정 백업"))
        layout.addWidget(QPushButton("설정 복원"))
        layout.addWidget(QPushButton("시스템 상태 보기"))

        tab.setLayout(layout)
        return tab

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ControlGUI()
    gui.show()
    sys.exit(app.exec_())

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QCheckBox, QTabWidget, QLineEdit, QListWidget,
    QSpinBox, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from utils.roi_io import load_roi
from utils.alert_utils import get_sound_list, load_alert_config, play_alert_sound
from utils.model_utils import get_model_list
from widgets.popup_widget import PopupPreviewWidget
from VehicleDetector import run_detection

DEFAULT_PROFILE = "default"

class DetectionThread(QThread):
    finished = pyqtSignal()

    def __init__(self, profile_name, volume, duration, auto_exit):
        super().__init__()
        self.profile_name = profile_name
        self.volume = volume
        self.duration = duration
        self.auto_exit = auto_exit
        self._running = True

    def run(self):
        run_detection(self.profile_name, self.stop_check, self.volume, self.duration)
        self.finished.emit()
        if self.auto_exit:
            os._exit(0)

    def stop_check(self):
        return not self._running

    def stop(self):
        self._running = False


class ControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("차량 감지 제어판")
        self.setGeometry(200, 200, 800, 600)
        self.profile_name = DEFAULT_PROFILE
        self.alert_config = load_alert_config(self.profile_name)

        self.tabs = QTabWidget()
        self.detect_tab = QWidget()
        self.alert_tab = QWidget()
        self.system_tab = QWidget()

        self.tabs.addTab(self.detect_tab, "감지")
        self.tabs.addTab(self.alert_tab, "알림 설정")
        self.tabs.addTab(self.system_tab, "시스템")

        self.init_detect_tab()
        self.init_alert_tab()
        self.init_system_tab()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.detector_thread = None
        self.running = False

    def init_detect_tab(self):
        self.detect_btn = QPushButton("차량 감지 시작")
        self.detect_btn.clicked.connect(self.toggle_detection)

        self.status_label = QLabel("상태: 대기 중")
        self.auto_exit_check = QCheckBox("감지 종료 후 프로그램 종료")
        self.roi_check = QCheckBox("ROI 표시 켜기")

        self.view_log_btn = QPushButton("로그 열기")
        self.view_log_btn.clicked.connect(self.open_log_dir)

        self.quit_btn = QPushButton("종료")
        self.quit_btn.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.detect_btn)
        layout.addWidget(self.status_label)
        layout.addWidget(self.auto_exit_check)
        layout.addWidget(self.roi_check)
        layout.addWidget(self.view_log_btn)
        layout.addWidget(self.quit_btn)
        self.detect_tab.setLayout(layout)

    def init_alert_tab(self):
        self.volume_label = QLabel("음량 (0.0~1.0):")
        self.volume_input = QLineEdit(str(self.alert_config.get("volume", 0.8)))
        self.volume_input.textChanged.connect(self.update_preview)

        self.duration_label = QLabel("지속 시간 (초):")
        self.duration_input = QLineEdit(str(self.alert_config.get("duration", 2)))
        self.duration_input.textChanged.connect(self.update_preview)

        self.sound_list = QListWidget()
        self.sound_list.addItems(get_sound_list())
        default_sound = self.alert_config.get("sound")
        if default_sound:
            items = self.sound_list.findItems(default_sound, Qt.MatchExactly)
            if items:
                self.sound_list.setCurrentItem(items[0])

        self.sound_list.itemSelectionChanged.connect(self.update_preview)

        self.play_sound_btn = QPushButton("선택한 소리 재생")
        self.play_sound_btn.clicked.connect(self.preview_sound)

        # 미리보기 위젯: profile_name 대신 config를 넘겨서 초기 설정을 표시
        self.popup_preview = PopupPreviewWidget(config=self.alert_config)
        self.popup_preview.setFixedHeight(150)

        layout = QVBoxLayout()
        layout.addWidget(self.volume_label)
        layout.addWidget(self.volume_input)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration_input)
        layout.addWidget(QLabel("사용 가능한 알림음:"))
        layout.addWidget(self.sound_list)
        layout.addWidget(self.play_sound_btn)
        layout.addWidget(QLabel("알림창 미리보기:"))
        layout.addWidget(self.popup_preview)
        self.alert_tab.setLayout(layout)

        self.update_preview()

    def init_system_tab(self):
        self.fps_label = QLabel("감지 FPS:")
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(8)

        self.model_label = QLabel("모델 선택:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(get_model_list())

        layout = QVBoxLayout()
        layout.addWidget(self.fps_label)
        layout.addWidget(self.fps_spin)
        layout.addWidget(self.model_label)
        layout.addWidget(self.model_combo)
        self.system_tab.setLayout(layout)

    def toggle_detection(self):
        if not self.running:
            roi = load_roi()
            if roi is None:
                QMessageBox.warning(self, "오류", "ROI 영역이 설정되지 않았습니다.")
                return

            try:
                volume = float(self.volume_input.text())
                duration = float(self.duration_input.text())
            except ValueError:
                QMessageBox.warning(self, "입력 오류", "음량과 지속 시간은 숫자여야 합니다.")
                return

            auto_exit = self.auto_exit_check.isChecked()
            self.detector_thread = DetectionThread(self.profile_name, volume, duration, auto_exit)
            self.detector_thread.finished.connect(self.on_detection_finished)
            self.detector_thread.start()
            self.detect_btn.setText("차량 감지 중지")
            self.status_label.setText("상태: 감지 중")
            self.running = True
        else:
            if self.detector_thread:
                self.detector_thread.stop()
                self.detector_thread.wait()
            self.detect_btn.setText("차량 감지 시작")
            self.status_label.setText("상태: 대기 중")
            self.running = False

    def on_detection_finished(self):
        if not self.auto_exit_check.isChecked():
            self.status_label.setText("상태: 종료됨")
            self.detect_btn.setText("차량 감지 시작")
            self.running = False

    def open_log_dir(self):
        log_dir = os.path.abspath("logs")
        os.makedirs(log_dir, exist_ok=True)
        os.startfile(log_dir)

    def preview_sound(self):
        selected = self.sound_list.currentItem()
        if selected:
            sound_name = selected.text()
            play_alert_sound(sound_name, float(self.volume_input.text()), float(self.duration_input.text()))

    def update_preview(self):
        config = {
            "volume": float(self.volume_input.text()) if self.volume_input.text() else 0.8,
            "duration": float(self.duration_input.text()) if self.duration_input.text() else 2,
            "sound": self.sound_list.currentItem().text() if self.sound_list.currentItem() else "",
            "message": "차량이 감지되었습니다.",
            "title": "차량 감지 알림!",
            "width": 300,
            "height": 100,
            "bg_color": "#ffffcc",
            "enabled": True
        }
        self.popup_preview.update_preview(config)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ControlGUI()
    gui.show()
    sys.exit(app.exec_())

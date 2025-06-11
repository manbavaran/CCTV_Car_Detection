import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QCheckBox, QSlider, QSpinBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

from utils.ROI_IO import load_roi
from VehicleDetector import run_detection
from utils.Logger import log_event

class DetectionThread(QThread):
    finished = pyqtSignal()

    def __init__(self, profile_name, volume, duration_sec):
        super().__init__()
        self.profile_name = profile_name
        self.volume = volume
        self.duration_sec = duration_sec
        self._running = True

    def run(self):
        log_event(f"{self.profile_name} 감지 시작")
        run_detection(
            self.profile_name,
            load_roi(),
            self.volume,
            self.duration_sec,
            self.stop_check
        )
        self.finished.emit()

    def stop_check(self):
        return not self._running

    def stop(self):
        self._running = False

class ControlGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("차량 감지 제어판")
        self.setGeometry(200, 200, 400, 350)

        self.status_label = QLabel("상태: 대기 중")
        self.detect_btn = QPushButton("차량 감지 시작")
        self.detect_btn.clicked.connect(self.toggle_detection)

        self.roi_check = QCheckBox("ROI 표시 켜기")

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_label = QLabel("볼륨: 80%")
        self.volume_slider.valueChanged.connect(self.update_volume_label)

        self.duration_box = QSpinBox()
        self.duration_box.setRange(1, 10)
        self.duration_box.setValue(2)
        self.duration_label = QLabel("지속시간 (초):")

        self.view_log_btn = QPushButton("로그 열기")
        self.view_log_btn.clicked.connect(self.open_log_dir)

        self.quit_btn = QPushButton("종료")
        self.quit_btn.clicked.connect(self.close)

        # 레이아웃 구성
        vbox = QVBoxLayout()
        vbox.addWidget(self.status_label)
        vbox.addWidget(self.detect_btn)
        vbox.addWidget(self.roi_check)
        vbox.addWidget(self.volume_label)
        vbox.addWidget(self.volume_slider)

        hbox_duration = QHBoxLayout()
        hbox_duration.addWidget(self.duration_label)
        hbox_duration.addWidget(self.duration_box)
        vbox.addLayout(hbox_duration)

        vbox.addWidget(self.view_log_btn)
        vbox.addWidget(self.quit_btn)
        self.setLayout(vbox)

        self.detector_thread = None
        self.running = False

    def update_volume_label(self):
        value = self.volume_slider.value()
        self.volume_label.setText(f"볼륨: {value}%")

    def toggle_detection(self):
        if not self.running:
            roi = load_roi()
            if roi is None:
                QMessageBox.warning(self, "오류", "ROI 영역이 설정되지 않았습니다.")
                return

            volume = self.volume_slider.value() / 100.0
            duration = self.duration_box.value()

            self.detector_thread = DetectionThread("default", volume, duration)
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
            log_event("감지 중지됨")

    def on_detection_finished(self):
        self.status_label.setText("상태: 종료됨")
        self.detect_btn.setText("차량 감지 시작")
        self.running = False

    def open_log_dir(self):
        log_dir = os.path.abspath("logs")
        os.makedirs(log_dir, exist_ok=True)
        os.startfile(log_dir)

    def closeEvent(self, event):
        if self.running and self.detector_thread:
            self.detector_thread.stop()
            self.detector_thread.wait()
        log_event("프로그램 종료")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ControlGUI()
    gui.show()
    sys.exit(app.exec_())

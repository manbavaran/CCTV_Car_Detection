import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QMessageBox
from VehicleDetector import VehicleDetector

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CCTV 차량 감지 시스템")
        self.setGeometry(300, 200, 400, 250)

        self.status_label = QLabel("상태: 대기 중")
        self.btn_start = QPushButton("감지 시작")
        self.btn_stop = QPushButton("감지 중지")
        self.btn_roi = QPushButton("ROI 설정")
        self.btn_exit = QPushButton("종료")

        self.btn_stop.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_roi)
        layout.addWidget(self.btn_exit)
        self.setLayout(layout)

        self.btn_start.clicked.connect(self.start_detection)
        self.btn_stop.clicked.connect(self.stop_detection)
        self.btn_roi.clicked.connect(self.open_roi_setting)
        self.btn_exit.clicked.connect(self.close)

        self.detector = None

    def start_detection(self):
        if self.detector is None:
            self.detector = VehicleDetector()
            self.detector.show()
            self.status_label.setText("상태: 감지 중")
            self.btn_start.setEnabled(False)
            self.btn_stop.setEnabled(True)
        else:
            QMessageBox.information(self, "알림", "이미 감지 중입니다.")

    def stop_detection(self):
        if self.detector is not None:
            self.detector.close()
            self.detector = None
            self.status_label.setText("상태: 대기 중")
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)

    def open_roi_setting(self):
        script_path = os.path.join(os.path.dirname(__file__), 'ROI_Four_Dots.py')
        subprocess.Popen(
            [sys.executable, script_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

    def closeEvent(self, event):
        if self.detector is not None:
            self.detector.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

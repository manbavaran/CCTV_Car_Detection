import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox

from VehicleDetector import VehicleDetector
from VirtualCamSender import VirtualCamSender

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("차량 감지 시스템")
        self.setGeometry(100, 100, 600, 400)

        self.detect_btn = QPushButton("감지 시작", self)
        self.stop_btn = QPushButton("감지 중지", self)
        self.roi_btn = QPushButton("ROI 설정", self)
        self.preview_btn = QPushButton("미리보기", self)
        self.close_btn = QPushButton("종료", self)

        self.detect_btn.clicked.connect(self.start_detection)
        self.stop_btn.clicked.connect(self.stop_detection)
        self.roi_btn.clicked.connect(self.open_roi_setter)
        self.preview_btn.clicked.connect(self.open_preview)
        self.close_btn.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.detect_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.roi_btn)
        layout.addWidget(self.preview_btn)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)

        self.detector_window = None
        self.preview_window = None

    def start_detection(self):
        if self.detector_window is None:
            self.detector_window = VehicleDetector()
            self.detector_window.show()
        else:
            QMessageBox.information(self, "알림", "이미 감지 중입니다.")

    def stop_detection(self):
        if self.detector_window is not None:
            self.detector_window.close()
            self.detector_window = None

    def open_preview(self):
        if self.preview_window is None:
            self.preview_window = VirtualCamSender()
            self.preview_window.show()
        else:
            QMessageBox.information(self, "알림", "이미 미리보기가 열려 있습니다.")

    def open_roi_setter(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, 'frozen', False):
            # exe로 실행 중이면 ROI_Four_Dots.exe 실행
            exe_path = os.path.join(base_dir, "ROI_Four_Dots.exe")
            if not os.path.exists(exe_path):
                QMessageBox.critical(self, "오류", f"ROI_Four_Dots.exe가 {exe_path}에 없습니다.\n빌드 후 dist 폴더에 함께 넣어주세요.")
                return
            subprocess.Popen([exe_path])
        else:
            # py로 실행 중이면 python ROI_Four_Dots.py 실행
            py_path = os.path.join(base_dir, "ROI_Four_Dots.py")
            subprocess.Popen([sys.executable, py_path])

    def closeEvent(self, event):
        if self.detector_window is not None:
            self.detector_window.close()
        if self.preview_window is not None:
            self.preview_window.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

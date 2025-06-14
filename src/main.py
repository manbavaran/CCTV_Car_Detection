import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from VehicleDetector import VehicleDetector
from VirtualCamSender import VideoWindow  # 이름 확인!
# from VirtualCamSender import VirtualCamSender  # 클래스명이 VideoWindow로 바뀜

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("차량 감지 시스템")
        self.setGeometry(100, 100, 430, 420)

        # 버튼 생성
        self.detect_btn = QPushButton("감지 시작")
        self.stop_btn = QPushButton("감지 중지")
        self.roi_btn = QPushButton("ROI 설정")
        self.preview_btn = QPushButton("미리보기")
        self.close_btn = QPushButton("종료")
        
        

        # 버튼 크기 통일
        for btn in [self.detect_btn, self.stop_btn, self.roi_btn, self.preview_btn, self.close_btn]:
            btn.setFixedWidth(180)
            btn.setFixedHeight(36)
            btn.setStyleSheet("font-size:16px;")

        # 버튼 시그널 연결
        self.detect_btn.clicked.connect(self.start_detection)
        self.stop_btn.clicked.connect(self.stop_detection)
        self.roi_btn.clicked.connect(self.open_roi_setter)
        self.preview_btn.clicked.connect(self.open_preview)
        self.close_btn.clicked.connect(self.close)


        # 버튼을 가운데 정렬된 레이아웃에 배치
        layout = QVBoxLayout()
        layout.addStretch(1)
        for btn in [self.detect_btn, self.stop_btn, self.roi_btn, self.preview_btn, self.close_btn]:
            row = QHBoxLayout()
            row.addStretch(1)
            row.addWidget(btn)
            row.addStretch(1)
            layout.addLayout(row)
            layout.addSpacing(9)
        layout.addStretch(1)
        self.setLayout(layout)

        self.detector_window = None
        self.preview_window = None
        
    def start_detection(self):
        if self.detector_window is None:
            self.detector_window = VehicleDetector()
            self.detector_window.closed.connect(self.stop_detection)
            self.detector_window.show()
        else:
            QMessageBox.information(self, "알림", "이미 감지 중입니다.")

    def stop_detection(self):
        if self.detector_window is not None:
            self.detector_window.close()
            self.detector_window = None

    def open_preview(self):
        if self.preview_window is None:
            self.preview_window = VideoWindow()
            self.preview_window.closed.connect(self.close_preview)
            self.preview_window.show()
        else:
            QMessageBox.information(self, "알림", "이미 미리보기가 열려 있습니다.")
    
    def close_preview(self):
        if self.preview_window is None:
            self.preview_window.close()
            self.preview_window = None

    def open_roi_setter(self):
        base_dir = os.getcwd()
        if getattr(sys, 'frozen', False):
            exe_path = os.path.join(base_dir, "ROI_Four_Dots.exe")
            if not os.path.exists(exe_path):
                QMessageBox.critical(
                    self, "오류",
                    f"ROI_Four_Dots.exe가 {exe_path}에 없습니다.\n빌드 후 dist 폴더에 함께 넣어주세요."
                )
                return
            subprocess.Popen([exe_path])
        else:
            py_path = os.path.join(base_dir, "ROI_Four_Dots.py")
            subprocess.Popen([sys.executable, py_path])
            
    def close_roi_setter(self):
        if self.close_roi_setter is None:
            self.close_roi_setter.close()
            self.close_roi_setter = None

    def closeEvent(self, event):
        if self.detector_window is not None:
            self.detector_window.close()
            self.detector_window = None
            
        if self.preview_window is not None:
            self.preview_window.close()
            self.preview_window = None
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

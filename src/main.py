import sys
import os
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from VehicleDetector import VehicleDetector
from ROI_Four_Dots import ROIDrawer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # src/ 기준

class DetectionThread(QThread):
    error_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.detector = VehicleDetector()
        self.is_running = True

    def run(self):
        roi_points = self.detector.load_roi()
        if not roi_points or len(roi_points) != 4:
            self.error_signal.emit("ROI 좌표를 먼저 설정해주세요.")
            return

        import cv2

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error_signal.emit("카메라 열기 실패!")
            return

        roi_poly = [tuple(pt) for pt in roi_points]

        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                break

            disp_frame = frame.copy()
            cv2.polylines(disp_frame, [np.array(roi_poly, np.int32)], isClosed=True, color=(0,255,0), thickness=2)

            boxes, scores, class_ids = self.detector.detect(frame)
            detected = False
            for box, score, cls in zip(boxes, scores, class_ids):
                cx = int((box[0] + box[2]) / 2)
                cy = int((box[1] + box[3]) / 2)
                if cv2.pointPolygonTest(np.array(roi_poly, np.int32), (cx, cy), False) >= 0:
                    cv2.rectangle(disp_frame, (box[0], box[1]), (box[2], box[3]), (0,0,255), 2)
                    detected = True

            if detected:
                self.detector.play_alert()

            cv2.imshow("감지 화면 (ESC: 종료)", disp_frame)
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break

        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.is_running = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CCTV 차량 감지 시스템")
        self.setGeometry(100, 100, 400, 180)

        layout = QVBoxLayout()
        self.btn_roi = QPushButton("ROI 설정")
        self.btn_roi.clicked.connect(self.open_roi_drawer)
        layout.addWidget(self.btn_roi)

        self.btn_start = QPushButton("감지 시작")
        self.btn_start.clicked.connect(self.start_detection)
        layout.addWidget(self.btn_start)

        self.setLayout(layout)
        self.det_thread = None

    def open_roi_drawer(self):
        self.roi_window = ROIDrawer()
        self.roi_window.show()

    def start_detection(self):
        if self.det_thread is not None and self.det_thread.isRunning():
            QMessageBox.information(self, "안내", "이미 감지가 진행 중입니다.")
            return
        self.det_thread = DetectionThread()
        self.det_thread.error_signal.connect(self.show_error)
        self.det_thread.start()

    def show_error(self, message):
        QMessageBox.critical(self, "오류", message)

    def closeEvent(self, event):
        if self.det_thread and self.det_thread.isRunning():
            self.det_thread.stop()
            self.det_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

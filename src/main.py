import sys
import os
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from VehicleDetector import VehicleDetector
from ROI_Four_Dots import ROIDrawer

# ============================
# [경로 설정 안내]
# 1. py 파일이 src/ 폴더에 있을 때:
#    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
# 2. py 파일이 프로젝트 최상위에 있을 때(= exe와 같은 위치):
#    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ← src/ 폴더 기준

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
        self.detector = None

    def open_roi_drawer(self):
        self.roi_window = ROIDrawer()
        self.roi_window.show()

    def start_detection(self):
        self.detector = VehicleDetector()
        roi_points = self.detector.load_roi()
        if not roi_points or len(roi_points) != 4:
            QMessageBox.warning(self, "오류", "ROI 좌표를 먼저 설정해주세요.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.critical(self, "오류", "카메라 열기 실패!")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # ROI 사각형 표시
            roi_poly = [tuple(pt) for pt in roi_points]
            disp_frame = frame.copy()
            cv2.polylines(disp_frame, [np.array(roi_poly, np.int32)], isClosed=True, color=(0,255,0), thickness=2)

            # 차량 감지
            boxes, scores, class_ids = self.detector.detect(frame)
            detected = False
            for box, score, cls in zip(boxes, scores, class_ids):
                # ROI 영역 내에 있을 때만
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

import sys
import cv2
import torch
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import threading
from utils.ROI_IO import load_roi
from utils.Alert import trigger_alert
from utils.Logger import log_event

CAR_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck

class VehicleDetector(QWidget):
    def __init__(self, profile_name="default", volume=0.8, alert_duration=2.0):
        super().__init__()
        self.setWindowTitle("차량 감지 시스템")
        self.setGeometry(200, 200, 900, 600)

        self.profile_name = profile_name
        self.volume = volume
        self.alert_duration = alert_duration

        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
        self.model.conf = 0.4

        self.label = QLabel("초기화 중...")
        self.status = QLabel("상태: 대기 중")
        self.count_label = QLabel("차량 수: 0")
        self.image_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.status)
        layout.addWidget(self.count_label)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(1)  # 가상카메라 입력
        self.roi = load_roi()

        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(125)  # 8fps

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.status.setText("카메라 입력 없음")
            log_event("ERROR", "카메라 입력 없음")
            return

        orig = frame.copy()
        results = self.model(frame)
        detections = results.pred[0]

        count = 0
        for *xyxy, conf, cls in detections:
            if int(cls) in CAR_CLASSES:
                cx = int((xyxy[0] + xyxy[2]) / 2)
                cy = int((xyxy[1] + xyxy[3]) / 2)
                if self.is_inside_roi((cx, cy)):
                    count += 1
                    cv2.rectangle(orig, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)

        self.status.setText("상태: 감지 중")
        self.count_label.setText(f"차량 수: {count}")

        if count > 0:
            log_event("ALERT", f"차량 감지 - 프로필: {self.profile_name}")
            threading.Thread(
                target=trigger_alert,
                args=(self.profile_name, self.volume, self.alert_duration),
                daemon=True
            ).start()

        img = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(800, 450, aspectRatioMode=1))

    def is_inside_roi(self, point):
        if len(self.roi) == 4:
            return cv2.pointPolygonTest(self.roi, point, False) >= 0
        return False

    def closeEvent(self, event):
        self.cap.release()
        log_event("INFO", "차량 감지 시스템 종료")
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = VehicleDetector()
    win.show()
    sys.exit(app.exec_())

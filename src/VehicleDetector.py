# src/VehicleDetector.py

import sys
import cv2
import torch
import numpy as np
import os
import time
import threading
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

from utils.roi_io import load_roi
from utils.alert import trigger_alert
from utils.logger import log_event

CAR_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck


class VehicleDetector(QWidget):
    def __init__(self, profile_name="default", volume=0.8, duration=3, cooldown=5, model_path="yolov5n"):
        super().__init__()
        self.setWindowTitle("차량 감지 시스템")
        self.setGeometry(200, 200, 900, 600)

        self.profile_name = profile_name
        self.volume = volume
        self.duration = duration
        self.cooldown = cooldown
        self.last_alert_time = 0

        # 모델 로드
        self.model = torch.hub.load('ultralytics/yolov5', model_path, pretrained=True)
        self.model.conf = 0.4

        # UI 요소
        self.label = QLabel(f"프로필: {self.profile_name}")
        self.status = QLabel("상태: 대기 중")
        self.count_label = QLabel("차량 수: 0")
        self.image_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.status)
        layout.addWidget(self.count_label)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # ROI 정보
        self.roi = load_roi()
        if self.roi is None or len(self.roi) != 4:
            QMessageBox.critical(self, "오류", "ROI 정보가 올바르지 않습니다. 설정 후 다시 실행해주세요.")
            self.close()
            return

        # 카메라 연결
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "카메라 오류", "가상카메라를 열 수 없습니다.")
            self.close()
            return

        # 타이머 시작 (8fps)
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(125)

        log_event(self.profile_name, "감지 시작")

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.status.setText("카메라 입력 없음")
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
                    cv2.rectangle(orig, (int(xyxy[0]), int(xyxy[1])),
                                  (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 2)

        self.status.setText("상태: 감지 중")
        self.count_label.setText(f"차량 수: {count}")

        now = time.time()
        if count > 0 and now - self.last_alert_time > self.cooldown:
            threading.Thread(
                target=trigger_alert,
                args=(self.profile_name, self.volume, self.duration),
                daemon=True
            ).start()
            self.last_alert_time = now

        img = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        qimg = QImage(img.data, w, h, ch * w, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(800, 450, aspectRatioMode=1))

    def is_inside_roi(self, point):
        if len(self.roi) == 4:
            return cv2.pointPolygonTest(self.roi, point, False) >= 0
        return False

    def closeEvent(self, event):
        self.cap.release()
        log_event(self.profile_name, "감지 종료")
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = VehicleDetector()
    win.show()
    sys.exit(app.exec_())

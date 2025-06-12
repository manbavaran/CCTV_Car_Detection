import sys
import cv2
import torch
import numpy as np
import os
import time
import threading
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

from roi_io import load_roi, draw_roi
from logger import log_event

CAR_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck

def play_alert_sound(volume=0.8, duration=2):
    import pygame
    sound_path = os.path.join(os.path.dirname(__file__), "..", "resources", "sounds", "Car_Alarm.mp3")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()
        time.sleep(duration)
        pygame.mixer.music.stop()
    except Exception as e:
        print("알림음 재생 실패:", e)

class VehicleDetector(QWidget):
    def __init__(self, volume=0.8, duration=2, cooldown=5, model_path=None, fps=8):
        super().__init__()
        self.setWindowTitle("차량 감지 시스템")
        self.setGeometry(200, 200, 900, 600)

        self.volume = volume
        self.duration = duration
        self.cooldown = cooldown
        # 기본 경로 지정: src/models/yolov5n.pt (절대경로로 변환)
        if model_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, "models", "yolov5n.pt")
        self.model_path = model_path
        self.fps = fps
        self.last_alert_time = 0

        # 모델 로드 (허브 대신 로컬 경로 사용)
        try:
            self.model = torch.hub.load(
                'ultralytics/yolov5',
                'custom',
                path=self.model_path,
                source='local'
            )
            self.model.conf = 0.4
        except Exception as e:
            QMessageBox.critical(self, "모델 로드 실패", f"로컬 모델 로드 중 오류 발생:\n{self.model_path}\n\n{str(e)}")
            self.close()
            return

        # UI 요소
        self.status = QLabel("상태: 대기 중")
        self.count_label = QLabel("차량 수: 0")
        self.image_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.count_label)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # ROI 정보
        self.roi = load_roi()
        if self.roi is None or len(self.roi) != 4:
            QMessageBox.critical(self, "오류", "ROI 정보가 올바르지 않습니다. ROI 설정 후 감지를 시작하세요.")
            self.close()
            return

        # 카메라 연결 (OBS/가상캠 번호 1)
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "카메라 오류", "가상카메라를 열 수 없습니다.")
            self.close()
            return

        # 타이머 시작
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(int(1000 / self.fps))  # fps 조절

        log_event("INFO", "차량 감지 시작")

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

        # ROI 폴리라인 시각화
        orig = draw_roi(orig, self.roi, show=True)

        self.status.setText("상태: 감지 중")
        self.count_label.setText(f"차량 수: {count}")

        now = time.time()
        if count > 0 and now - self.last_alert_time > self.cooldown:
            threading.Thread(
                target=play_alert_sound,
                args=(self.volume, self.duration),
                daemon=True
            ).start()
            log_event("ALERT", "차량 감지 알림 발생")
            self.last_alert_time = now

        img = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        qimg = QImage(img.data, w, h, ch * w, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(800, 450, aspectRatioMode=1))

    def is_inside_roi(self, point):
        return cv2.pointPolygonTest(np.array(self.roi, dtype=np.int32), point, False) >= 0

    def closeEvent(self, event):
        self.cap.release()
        log_event("INFO", "차량 감지 종료")
        event.accept()

import sys
import cv2
import numpy as np
import os
import time
import threading
import onnxruntime as ort
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

from roi_io import load_roi, draw_roi
from logger import log_event

CAR_CLASSES = [2, 3, 5, 7]  # COCO: car, motorcycle, bus, truck

def play_alert_sound(volume=0.8, duration=2, total_time=5):
    """
    음원(mp3)을 total_time(초) 동안 반복 재생.
    duration: mp3 파일 한 번 재생 시간(초)
    total_time: 전체 재생 시간(초)
    """
    import pygame
    sound_path = os.path.join(os.path.dirname(__file__), "..", "resources", "sounds", "Car_Alarm.mp3")
    try:
        pygame.mixer.init()
        repeat = int(total_time / duration + 0.5)
        for _ in range(repeat):
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
            time.sleep(duration)
            pygame.mixer.music.stop()
    except Exception as e:
        print("알림음 재생 실패:", e)

def preprocess(frame, img_size=640):
    img = cv2.resize(frame, (img_size, img_size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.transpose(2, 0, 1)  # HWC→CHW
    img = np.ascontiguousarray(img, dtype=np.float32) / 255.0
    img = np.expand_dims(img, 0)
    return img

def xywh2xyxy(x, y, w, h):
    # x, y, w, h → x1, y1, x2, y2
    return [x - w / 2, y - h / 2, x + w / 2, y + h / 2]

def nms(boxes, scores, iou_threshold):
    # 간단 NMS. (YOLO ONNX 결과 후처리용)
    if len(boxes) == 0:
        return []
    boxes = np.array(boxes)
    scores = np.array(scores)
    indices = []
    idxs = scores.argsort()[::-1]
    while len(idxs) > 0:
        i = idxs[0]
        indices.append(i)
        xx1 = np.maximum(boxes[i, 0], boxes[idxs[1:], 0])
        yy1 = np.maximum(boxes[i, 1], boxes[idxs[1:], 1])
        xx2 = np.minimum(boxes[i, 2], boxes[idxs[1:], 2])
        yy2 = np.minimum(boxes[i, 3], boxes[idxs[1:], 3])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        inter = w * h
        area1 = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area2 = (boxes[idxs[1:], 2] - boxes[idxs[1:], 0]) * (boxes[idxs[1:], 3] - boxes[idxs[1:], 1])
        union = area1 + area2 - inter
        iou = inter / (union + 1e-6)

        idxs = idxs[1:][iou < iou_threshold]
    return indices

class VehicleDetector(QWidget):
    def __init__(self, volume=0.8, duration=2, total_time=5, cooldown=6, fps=5):
        super().__init__()
        self.setWindowTitle("차량 감지 시스템")
        self.setGeometry(200, 200, 900, 600)

        self.volume = volume
        self.duration = duration       # mp3 한 번 재생 길이(초)
        self.total_time = total_time   # 총 반복 재생 시간(초)
        self.cooldown = cooldown      # 연속 알림 방지 시간(초)
        self.fps = fps                # 프레임 처리 속도(초당)
        self.last_alert_time = 0

        # 모델 로드 (ONNX)
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            onnx_path = os.path.join(base_dir, "models", "yolov5n.onnx")
            self.ort_session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        except Exception as e:
            QMessageBox.critical(self, "모델 로드 실패", f"ONNX 모델 로드 중 오류:\n{str(e)}")
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
        img_input = preprocess(frame, img_size=640)
        outputs = self.ort_session.run(None, {"images": img_input})

        # YOLOv5 ONNX outputs[0] shape: (1, 25200, 85)
        pred = outputs[0][0]
        boxes = []
        scores = []
        classes = []
        conf_thres = 0.4
        iou_thres = 0.45
        img_h, img_w = frame.shape[:2]

        for det in pred:
            obj_conf = det[4]
            class_confs = det[5:]
            class_id = np.argmax(class_confs)
            conf = obj_conf * class_confs[class_id]
            if conf > conf_thres and class_id in CAR_CLASSES:
                x, y, w, h = det[0:4]
                box = xywh2xyxy(x, y, w, h)
                # 이미지 크기 보정
                box = [
                    int(box[0] / 640 * img_w),
                    int(box[1] / 640 * img_h),
                    int(box[2] / 640 * img_w),
                    int(box[3] / 640 * img_h)
                ]
                boxes.append(box)
                scores.append(float(conf))
                classes.append(class_id)

        # NMS
        nms_idx = nms(boxes, scores, iou_thres)
        count = 0
        for i in nms_idx:
            box = boxes[i]
            class_id = classes[i]
            # 박스 중심점 계산 (ROI 포함여부)
            cx = int((box[0] + box[2]) / 2)
            cy = int((box[1] + box[3]) / 2)
            if self.is_inside_roi((cx, cy)):
                count += 1
                cv2.rectangle(orig, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

        # ROI 폴리라인 시각화
        orig = draw_roi(orig, self.roi, show=True)

        self.status.setText("상태: 감지 중")
        self.count_label.setText(f"차량 수: {count}")

        now = time.time()
        if count > 0 and now - self.last_alert_time > self.cooldown:
            threading.Thread(
                target=play_alert_sound,
                args=(self.volume, self.duration, self.total_time),  # 5초 동안 반복
                daemon=True
            ).start()
            log_event("ALERT", "차량 감지 알림 발생")
            self.last_alert_time = now

        img_rgb = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        qimg = QImage(img_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(800, 450, aspectRatioMode=1))

    def is_inside_roi(self, point):
        return cv2.pointPolygonTest(np.array(self.roi, dtype=np.int32), point, False) >= 0

    def closeEvent(self, event):
        self.cap.release()
        log_event("INFO", "차량 감지 종료")
        event.accept()

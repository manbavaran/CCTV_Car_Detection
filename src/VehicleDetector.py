import os
import cv2
import numpy as np
import onnxruntime as ort
import time
from playsound import playsound

# ============================
# [경로 설정 안내]
# 1. py 파일이 src/ 폴더에 있을 때:
#    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
# 2. py 파일이 프로젝트 최상위에 있을 때(= exe와 같은 위치):
#    base_dir = os.path.dirname(os.path.abspath(__file__))
# ============================

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ← src/ 폴더 기준

MODEL_PATH = os.path.join(base_dir, "models", "yolov5n.onnx")
SOUND_PATH = os.path.join(base_dir, "resources", "sounds", "Car_Alarm.mp3")
LOG_PATH = os.path.join(base_dir, "logs", "vehicle_detection.log")
ROI_PATH = os.path.join(base_dir, "profiles", "roi_points.pkl")

class VehicleDetector:
    def __init__(self):
        self.session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.cooldown = 0
        self.cooldown_time = 5.0  # seconds
        self.last_alert_time = 0
        self.sound_duration = 5.0  # seconds

    def preprocess(self, frame):
        img = cv2.resize(frame, (640, 640))
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR→RGB, HWC→CHW
        img = np.ascontiguousarray(img, dtype=np.float32) / 255.0
        img = np.expand_dims(img, 0)
        return img

    def detect(self, frame):
        input_tensor = self.preprocess(frame)
        outputs = self.session.run([self.output_name], {self.input_name: input_tensor})[0]
        # yolov5n onnx 기본 결과 (batch, nboxes, 85)
        # 85: 4(box), 1(obj conf), 80(class conf)
        boxes, scores, class_ids = self.postprocess(outputs, frame.shape)
        return boxes, scores, class_ids

    def postprocess(self, output, orig_shape, conf_thres=0.25, iou_thres=0.45):
        # [batch, 25200, 85]
        preds = output[0] if isinstance(output, (tuple, list, np.ndarray)) else output
        # conf: objectness * class_conf
        scores = preds[..., 4:5] * preds[..., 5:]
        class_ids = np.argmax(scores, axis=-1)
        confidences = np.max(scores, axis=-1)
        mask = confidences > conf_thres
        boxes = preds[..., :4][mask]
        confidences = confidences[mask]
        class_ids = class_ids[mask]
        # xywh → xyxy 변환
        if boxes.shape[0] > 0:
            boxes = self.xywh2xyxy(boxes, orig_shape)
        return boxes, confidences, class_ids

    def xywh2xyxy(self, boxes, orig_shape):
        # yolov5 onnx output은 xywh(0~640)
        h, w = orig_shape[:2]
        x = boxes[:, 0]
        y = boxes[:, 1]
        bw = boxes[:, 2]
        bh = boxes[:, 3]
        x1 = (x - bw / 2) * w / 640
        y1 = (y - bh / 2) * h / 640
        x2 = (x + bw / 2) * w / 640
        y2 = (y + bh / 2) * h / 640
        return np.stack([x1, y1, x2, y2], axis=-1).astype(np.int32)

    def play_alert(self):
        now = time.time()
        if now - self.last_alert_time > self.cooldown_time:
            self.last_alert_time = now
            # 5초 동안 반복 재생 (음원 길이와 무관)
            t_end = now + self.sound_duration
            while time.time() < t_end:
                playsound(SOUND_PATH, block=False)
                time.sleep(1.0)
            self.log_event("Alert sound played")

    def log_event(self, msg):
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")

    def load_roi(self):
        import pickle
        if not os.path.exists(ROI_PATH):
            return None
        with open(ROI_PATH, "rb") as f:
            return pickle.load(f)

import sys
import os
import cv2
import time
import threading
import numpy as np
import onnxruntime as ort
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QApplication
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, pyqtSignal

from roi_io import load_roi
from logger import log_event

CAR_CLASSES = [2, 3, 5, 7]  # COCO: car, motorcycle, bus, truck

def play_alert_sound(volume=1.0, duration=2, total_time=5):
    import pygame
    base_dir = os.getcwd()
    sound_path = os.path.join(base_dir, "resources", "sounds", "Car_Alarm.mp3")
    try:
        pygame.mixer.init()
        print("사운드 재생 시도 1")
        repeat = int(total_time / duration + 0.5)
        print("사운드 재생 시도 2")
        for _ in range(repeat):
            print("사운드 재생 시도 3")
            pygame.mixer.music.load(sound_path)
            print("사운드 재생 시도 4")
            pygame.mixer.music.set_volume(volume)
            print("사운드 재생 시도 5")
            pygame.mixer.music.play()
            print("사운드 재생 시도 6")
            time.sleep(duration)
            print("사운드 재생 시도 7")
            pygame.mixer.music.stop()
            print("사운드 재생 시도 8")
    except Exception as e:
        print("알림음 재생 실패:", e)

def preprocess(frame, img_size=640):
    img = cv2.resize(frame, (img_size, img_size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.transpose(2, 0, 1)
    img = np.ascontiguousarray(img, dtype=np.float32) / 255.0
    img = np.expand_dims(img, 0)
    return img

def xywh2xyxy(x, y, w, h):
    return [x - w / 2, y - h / 2, x + w / 2, y + h / 2]

def nms(boxes, scores, iou_threshold):
    if len(boxes) == 0:
        return []
    boxes = np.array(boxes)
    scores = np.array(scores)
    indices = []
    idxs = scores.argsort()[::-1]
    while len(idxs) > 0:
        i = idxs[0]
        indices.append(i)
        if len(idxs) == 1:
            break
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

def scale_points(points, src_size, dst_size):
    """원본 해상도의 점 리스트를, 표시창 해상도에 맞게 스케일 변환."""
    src_w, src_h = src_size
    dst_w, dst_h = dst_size
    scale_x = dst_w / src_w
    scale_y = dst_h / src_h
    return [(int(x * scale_x), int(y * scale_y)) for (x, y) in points]

def scale_box(box, src_size, dst_size):
    """원본 해상도의 박스([x1, y1, x2, y2])를, 표시창 해상도에 맞게 변환."""
    src_w, src_h = src_size
    dst_w, dst_h = dst_size
    scale_x = dst_w / src_w
    scale_y = dst_h / src_h
    x1 = int(box[0] * scale_x)
    y1 = int(box[1] * scale_y)
    x2 = int(box[2] * scale_x)
    y2 = int(box[3] * scale_y)
    return [x1, y1, x2, y2]

class VehicleDetector(QWidget):
    closed = pyqtSignal()
    def __init__(self, volume=1.0, duration=2, total_time=5, cooldown=15, fps=5):
        super().__init__()
        self.setWindowTitle("차량 감지 시스템")

        # 카메라 초기화 및 해상도 감지
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "카메라 오류", "카메라를 열 수 없습니다.")
            self.close()
            return
        ret, frame = self.cap.read()
        if not ret:
            QMessageBox.critical(self, "카메라 오류", "카메라 프레임을 읽을 수 없습니다.")
            self.cap.release()
            self.close()
            return
        self.orig_h, self.orig_w = frame.shape[:2]

        # ROI 정보 불러오기
        self.roi = load_roi()
        if self.roi is None or len(self.roi) != 4:
            QMessageBox.critical(self, "오류", "ROI 정보가 올바르지 않습니다. ROI 설정 후 감지를 시작하세요.")
            self.cap.release()
            self.close()
            return

        # ONNX 모델 로드
        try:
            base_dir = os.getcwd()
            onnx_path = os.path.join(base_dir, "models", "yolov5n.onnx")
            self.ort_session = ort.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
        except Exception as e:
            QMessageBox.critical(self, "모델 로드 실패", f"ONNX 모델 로드 중 오류:\n{str(e)}")
            self.cap.release()
            self.close()
            return

        # 알림/감지 변수
        self.volume = volume
        self.duration = duration
        self.total_time = total_time
        self.cooldown = cooldown
        self.fps = fps
        self.last_alert_time = 0
        self.is_alerting = False  # 알람 재생 상태 플래그

        # 이미지 출력 라벨 (최대화시 창 크기에 맞게 자동 리사이즈)
        self.image_label = QLabel(self)
        self.image_label.setScaledContents(True)  # 자동 리사이즈
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.showMaximized()  # 창 최대화

        # 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(int(1000 / self.fps))

        log_event("INFO", "차량 감지 시작")

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        orig = frame.copy()
        img_input = preprocess(frame, img_size=640)
        outputs = self.ort_session.run(None, {"images": img_input})

        pred = outputs[0][0]
        boxes, scores, classes = [], [], []
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
                box = [
                    int(box[0] / 640 * img_w),
                    int(box[1] / 640 * img_h),
                    int(box[2] / 640 * img_w),
                    int(box[3] / 640 * img_h)
                ]
                boxes.append(box)
                scores.append(float(conf))
                classes.append(class_id)

        nms_idx = nms(boxes, scores, iou_thres)
        count = 0
        for i in nms_idx:
            box = boxes[i]
            class_id = classes[i]
            cx = int((box[0] + box[2]) / 2)
            cy = int((box[1] + box[3]) / 2)
            if self.is_inside_roi((cx, cy)):
                count += 1
                # 박스는 창 크기에 맞게 스케일
                scaled_box = scale_box(box, (self.orig_w, self.orig_h),
                                            (self.image_label.width(), self.image_label.height()))
                cv2.rectangle(orig, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)

        # 라벨 크기에 맞춰 프레임 리사이즈
        label_w = self.image_label.width()
        label_h = self.image_label.height()
        disp_img = cv2.resize(orig, (label_w, label_h), interpolation=cv2.INTER_AREA)

        # ROI(네 점)도 라벨 크기에 맞게 변환해서 그림
        scaled_roi = scale_points(self.roi, (self.orig_w, self.orig_h), (label_w, label_h))
        if scaled_roi and len(scaled_roi) == 4:
            pts = np.array(scaled_roi, dtype=np.int32)
            cv2.polylines(disp_img, [pts], isClosed=True, color=(0,255,0), thickness=2)

        img_rgb = cv2.cvtColor(disp_img, cv2.COLOR_BGR2RGB)
        qimg = QImage(img_rgb.data, label_w, label_h, 3 * label_w, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg))

        now = time.time()
        # 알람 재생 중이 아니고, 쿨타임이 지났을 때만 알람 재생
        if count > 0 and (now - self.last_alert_time > 20) and not self.is_alerting:
            self.is_alerting = True
            def finish_alert():
                play_alert_sound(self.volume, self.duration, self.total_time)  # 5초
                self.last_alert_time = time.time()  # "알람 끝난 직후" 기준으로 쿨타임 갱신
                self.is_alerting = False
            threading.Thread(target=finish_alert, daemon=True).start()
            log_event("ALERT", "차량 감지 알림 발생")       

    def is_inside_roi(self, point):
        # point는 원본 해상도 기준이어야 함
        return cv2.pointPolygonTest(np.array(self.roi, dtype=np.int32), point, False) >= 0

    def closeEvent(self, event):
        self.closed.emit()  # X버튼
        log_event("INFO", "차량 감지 종료")
        event.accept()

    def keyPressEvent(self, event):
        # ESC 또는 Q 키로 창 닫기
        if event.key() in (Qt.Key_Escape, Qt.Key_Q):
            self.closed.emit()  # ESC, Q키
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VehicleDetector()
    win.show()
    sys.exit(app.exec_())

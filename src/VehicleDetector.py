import cv2
import time
import numpy as np
from ultralytics import YOLO
from datetime import datetime
import os
import logging
from playsound import playsound

VEHICLE_CLASSES = {2, 5, 7}  # car, bus, truck


def load_yolo_model(model_path="models/yolov5n.pt"):
    return YOLO(model_path)


def verify_vehicle(frame, roi_points, model, last_infer_time, interval_sec=0.125):
    now = time.time()
    if now - last_infer_time < interval_sec:
        return False, last_infer_time

    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [roi_points], 255)
    roi_only = cv2.bitwise_and(frame, frame, mask=mask)

    results = model(roi_only, verbose=False)
    for result in results:
        for cls in result.boxes.cls:
            if int(cls) in VEHICLE_CLASSES:
                return True, now
    return False, now


def create_roi_mask(frame_shape, roi_points):
    mask = np.zeros(frame_shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [roi_points], 255)
    return mask


def detect_motion(prev, curr, mask):
    diff = cv2.absdiff(prev, curr)
    diff = cv2.bitwise_and(diff, diff, mask=mask)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    return thresh


def is_large_movement(thresh, area_thresh=3000):
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) > area_thresh:
            return True
    return False


def init_log_file(profile_name):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{profile_name}_{datetime.now():%Y%m%d}.log")

    logger = logging.getLogger("vehicle_logger")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_vehicle_detection(profile_name):
    logger = logging.getLogger("vehicle_logger")
    logger.info(f"차량 감지됨 - 프로필: {profile_name}")


def trigger_alert(profile_name):
    log_vehicle_detection(profile_name)
    print("🚨 차량 감지됨! 알림 발생")
    try:
        sound_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sounds', 'alert.mp3')
        playsound(sound_path)
    except Exception as e:
        print("소리 재생 실패:", e)


def run_detection(profile_name, roi_points):
    init_log_file(profile_name)
    model = load_yolo_model()
    last_infer_time = 0

    cap = cv2.VideoCapture(0)
    assert cap.isOpened(), "❌ 가상카메라를 열 수 없습니다."

    ret, frame = cap.read()
    if not ret:
        return

    roi_mask = create_roi_mask(frame.shape, roi_points)
    prev = cv2.cvtColor(cv2.GaussianBlur(frame, (5, 5), 0), cv2.COLOR_BGR2GRAY)

    last_alert_time = 0
    cooldown_sec = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(cv2.GaussianBlur(frame, (5, 5), 0), cv2.COLOR_BGR2GRAY)
        thresh = detect_motion(prev, gray, roi_mask)

        if is_large_movement(thresh):
            now = time.time()
            if now - last_alert_time > cooldown_sec:
                found, last_infer_time = verify_vehicle(frame, roi_points, model, last_infer_time)
                if found:
                    trigger_alert(profile_name)
                    last_alert_time = now

        prev = gray.copy()
        cv2.imshow("CCTV View", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

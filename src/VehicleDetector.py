# src/VehicleDetector.py
import cv2
import numpy as np
import time
import os
from datetime import datetime
from utils.ROI_IO import load_roi
from ultralytics import YOLO

# 차량 클래스 ID (COCO 기준)
VEHICLE_CLASSES = {2, 3, 5, 7}  # car, motorcycle, bus, truck

# 알림음 및 로그 기록
from playsound import playsound

def trigger_alert():
    try:
        sound_path = os.path.join("resources", "sounds", "alert.mp3")
        playsound(sound_path)
    except Exception as e:
        print("[오류] 소리 재생 실패:", e)

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "alerts.log")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now}] 차량 감지됨\n")

# ROI 내 포함 여부 확인
def is_inside_roi(point, roi):
    if len(roi) == 4:
        return cv2.pointPolygonTest(np.array(roi, dtype=np.int32), point, False) >= 0
    return False

# 메인 감지 루프
def run_detection(profile_name, stop_flag_func=None):
    roi = load_roi()
    if roi is None:
        print("❌ ROI를 불러올 수 없습니다.")
        return

    cap = cv2.VideoCapture(1)  # OBS 가상카메라
    assert cap.isOpened(), "❌ 가상카메라 열기 실패"

    model = YOLO("models/yolov5n.pt")
    model.fuse()

    last_alert_time = 0
    cooldown = 5  # 초 단위

    while True:
        if stop_flag_func and stop_flag_func():
            print("[ℹ] 감지 루프 종료 요청 수신")
            break

        ret, frame = cap.read()
        if not ret:
            continue

        results = model(frame, verbose=False)[0]

        vehicle_detected = False
        for box in results.boxes:
            cls = int(box.cls[0])
            if cls in VEHICLE_CLASSES:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                if is_inside_roi((cx, cy), roi):
                    vehicle_detected = True
                    break

        now = time.time()
        if vehicle_detected and now - last_alert_time > cooldown:
            print("[🚗] 차량 감지됨!")
            trigger_alert()
            last_alert_time = now

    cap.release()
    print("[✅] 감지 루프 종료")

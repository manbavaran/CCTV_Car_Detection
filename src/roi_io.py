import os
import pickle
from datetime import datetime
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROI_DIR = os.path.join(BASE_DIR, "profiles")
ROI_PATH = os.path.join(ROI_DIR, "roi_points.pkl")
LOG_DIR = os.path.join(BASE_DIR, "logs", "roi")

def save_roi(points):
    os.makedirs(ROI_DIR, exist_ok=True)
    with open(ROI_PATH, "wb") as f:
        pickle.dump(points, f)
    log_roi_save()

def load_roi():
    if os.path.exists(ROI_PATH):
        with open(ROI_PATH, "rb") as f:
            return pickle.load(f)
    return None

def log_roi_save():
    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.now()
    log_file = os.path.join(LOG_DIR, f"{now:%Y-%m-%d}.log")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ROI 저장: {os.path.abspath(ROI_PATH)}\n")

def draw_roi(frame, roi_points, show=True, color=(0, 255, 0), thickness=2):
    if show and roi_points is not None and len(roi_points) == 4:
        roi_pts = np.array(roi_points, dtype=np.int32).reshape(-1, 1, 2)
        cv2.polylines(frame, [roi_pts], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)
    return frame

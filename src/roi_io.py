import os
import pickle
from datetime import datetime
import cv2
import numpy as np

# 프로젝트 루트 기준 절대경로 계산
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROI_DIR = os.path.join(BASE_DIR, "profiles")
ROI_PATH = os.path.join(ROI_DIR, "roi_points.pkl")
LOG_DIR = os.path.join(BASE_DIR, "logs", "roi")

def save_roi(points):
    """점 네 개로 이루어진 ROI 좌표(리스트) 저장 + 로그"""
    os.makedirs(ROI_DIR, exist_ok=True)
    with open(ROI_PATH, "wb") as f:
        pickle.dump(points, f)
    log_roi_save()

def load_roi():
    """ROI 좌표(리스트) 불러오기. 없으면 None"""
    if os.path.exists(ROI_PATH):
        with open(ROI_PATH, "rb") as f:
            return pickle.load(f)
    return None

def log_roi_save():
    """ROI 저장 로그를 기록"""
    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.now()
    log_file = os.path.join(LOG_DIR, f"{now:%Y-%m-%d}.log")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ROI 저장: {os.path.abspath(ROI_PATH)}\n")

def draw_roi(frame, roi_points, show=True, color=(0, 255, 0), thickness=2):
    """
    ROI(사각형) 폴리라인을 프레임 위에 그려 반환.
    - frame: OpenCV 이미지(ndarray)
    - roi_points: 점 리스트 [(x, y), ...]
    - show: True면 그림
    """
    if show and roi_points is not None and len(roi_points) == 4:
        roi_pts = np.array(roi_points, dtype=np.int32).reshape(-1, 1, 2)
        cv2.polylines(frame, [roi_pts], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)
    return frame

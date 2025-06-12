import os
import pickle
from datetime import datetime
import cv2
import numpy as np

# 프로젝트 루트 기준 디렉토리 경로 생성
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROI_DIR = os.path.join(BASE_DIR, "profiles")
LOG_DIR = os.path.join(BASE_DIR, "..", "logs", "roi")

def get_roi_path(profile_name="default"):
    """프로필 이름별 ROI 파일 절대 경로 반환 (.pkl)"""
    os.makedirs(ROI_DIR, exist_ok=True)
    return os.path.join(ROI_DIR, f"{profile_name}_roi.pkl")

def load_roi(profile_name="default"):
    """
    ROI 좌표(pickle) 불러오기
    - profile_name: 프로필명
    - return: ROI 점 리스트 또는 None
    """
    path = get_roi_path(profile_name)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def save_roi(points, profile_name="default"):
    """
    ROI 좌표(pickle) 저장 + 로그 기록
    - points: ROI 점 리스트 [(x, y), ...]
    - profile_name: 프로필명
    """
    path = get_roi_path(profile_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(points, f)
    log_roi_save(path, profile_name)

def log_roi_save(path, profile_name="default"):
    """ROI 저장 로그를 기록"""
    os.makedirs(LOG_DIR, exist_ok=True)
    now = datetime.now()
    log_file = os.path.join(LOG_DIR, f"{now:%Y-%m-%d}.log")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 프로필({profile_name}) ROI 저장됨: {os.path.abspath(path)}\n")

def draw_roi(frame, roi_points, show=True, color=(0, 255, 0), thickness=2):
    """
    ROI 다각형을 프레임에 그려 반환합니다.
    - frame: OpenCV 이미지(ndarray)
    - roi_points: (N, 2) ndarray 또는 list of (x, y)
    - show: True일 때만 ROI 표시
    """
    if show and roi_points is not None and len(roi_points) >= 3:
        roi_pts = np.array(roi_points, dtype=np.int32).reshape(-1, 1, 2)
        cv2.polylines(frame, [roi_pts], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)
    return frame

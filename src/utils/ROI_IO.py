import os
import pickle
from datetime import datetime

# ROI 좌표 불러오기
def load_roi(path="src/profiles/roi_points.pkl"):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

# ROI 좌표 저장 및 로그 기록
def save_roi(points, path="src/profiles/roi_points.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(points, f)
    log_roi_save(path)

# ROI 저장 로그 기록
def log_roi_save(path):
    log_dir = os.path.join("logs", "roi")
    os.makedirs(log_dir, exist_ok=True)

    now = datetime.now()
    log_file = os.path.join(log_dir, f"{now:%Y-%m-%d}.log")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ROI 저장됨: {os.path.abspath(path)}\n")

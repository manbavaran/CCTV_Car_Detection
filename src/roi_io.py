import os
import pickle
import datetime

# ============================
# [경로 설정 안내]
# 1. py 파일이 src/ 폴더에 있을 때:
#    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#
# 2. py 파일이 프로젝트 최상위에 있을 때(= exe와 같은 위치):
#    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # ← src/ 폴더 기준
ROI_DIR = os.path.join(BASE_DIR, "profiles")
LOG_DIR = os.path.join(BASE_DIR, "logs", "roi")

def ensure_dirs():
    os.makedirs(ROI_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

def save_roi(points, filename="roi_points.pkl"):
    """
    ROI 좌표(point list)를 저장합니다.
    """
    ensure_dirs()
    path = os.path.join(ROI_DIR, filename)
    with open(path, "wb") as f:
        pickle.dump(points, f)

    # 로그도 함께 남김 (시간, 좌표 기록)
    log_msg = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ROI 저장: {points}\n"
    log_path = os.path.join(LOG_DIR, "roi_save.log")
    with open(log_path, "a", encoding="utf-8") as logf:
        logf.write(log_msg)

def load_roi(filename="roi_points.pkl"):
    """
    ROI 좌표(point list)를 불러옵니다.
    """
    path = os.path.join(ROI_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        points = pickle.load(f)
    return points

def log_event(event: str):
    """
    기타 roi 관련 이벤트를 로그로 남깁니다.
    """
    ensure_dirs()
    log_path = os.path.join(LOG_DIR, "roi_events.log")
    log_msg = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event}\n"
    with open(log_path, "a", encoding="utf-8") as logf:
        logf.write(log_msg)

# 테스트용
if __name__ == '__main__':
    example_points = [(10, 20), (100, 200), (300, 400), (400, 100)]
    save_roi(example_points)
    loaded = load_roi()
    print("저장한 ROI:", loaded)
    log_event("테스트 이벤트")

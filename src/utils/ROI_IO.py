# utils/roi_io.py
import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROI_PATH = os.path.join(BASE_DIR, "profiles", "roi_points.pkl")

def load_roi(path=DEFAULT_ROI_PATH):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def save_roi(points, path=DEFAULT_ROI_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(points, f)

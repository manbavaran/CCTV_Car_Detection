# utils/roi_io.py
import pickle
import os

def load_roi(path="src/profiles/roi_points.pkl"):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

def save_roi(points, path="src/profiles/roi_points.pkl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(points, f)
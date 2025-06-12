# src/utils/roi_display.py

import cv2

_roi_visible = True

def toggle_roi_visibility():
    global _roi_visible
    _roi_visible = not _roi_visible

def is_roi_visible():
    return _roi_visible

def draw_roi(frame, roi_points, color=(0, 255, 0), thickness=2):
    if is_roi_visible() and roi_points is not None:
        cv2.polylines(frame, [roi_points], isClosed=True, color=color, thickness=thickness, lineType=cv2.LINE_AA)
    return frame

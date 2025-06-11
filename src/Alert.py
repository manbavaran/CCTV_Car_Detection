# src/alert.py
import os
from datetime import datetime
import pygame

pygame.mixer.init()

def play_alert_sound(volume=0.8):
    try:
        sound_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sounds', 'alert.mp3')
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()
    except Exception as e:
        print("[경고] 알림음 재생 실패:", e)

def log_alert(profile_name="default"):
    os.makedirs("logs", exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join("logs", "alerts.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now}] 차량 감지 - 프로필: {profile_name}\n")

def trigger_alert(profile_name="default", volume=0.8):
    play_alert_sound(volume)
    log_alert(profile_name)

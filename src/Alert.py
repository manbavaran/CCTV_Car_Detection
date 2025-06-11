# src/alert.py
import os
import pygame
from datetime import datetime

# 알림 초기화
def init_alert_system():
    pygame.mixer.init()

# 알림음 재생 함수
def play_alert(volume=1.0):
    try:
        alert_path = os.path.join("resources", "sounds", "alert.mp3")
        if not os.path.exists(alert_path):
            raise FileNotFoundError(f"🔊 알림음 파일이 없습니다: {alert_path}")
        sound = pygame.mixer.Sound(alert_path)
        sound.set_volume(volume)  # 0.0 (무음) ~ 1.0 (최대)
        sound.play()
    except Exception as e:
        print(f"[오류] 알림음 재생 실패: {e}")

# 로그 기록
def log_alert():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join(log_dir, "alerts.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{now}] 차량 감지 알림 발생\n")

# 알림 트리거 (음 + 로그)
def trigger_alert(volume=1.0):
    play_alert(volume)
    log_alert()
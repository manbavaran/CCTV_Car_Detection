import os
import pygame
from datetime import datetime

# 소리 재생 함수
def play_alert_sound(volume=0.8, duration_sec=2.0):
    try:
        pygame.mixer.init()
        sound_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sounds', 'alert.mp3')

        if not os.path.exists(sound_path):
            raise FileNotFoundError("알림 사운드 파일이 존재하지 않습니다.")

        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()

        pygame.time.delay(int(duration_sec * 1000))
        pygame.mixer.music.stop()

    except Exception as e:
        print("소리 재생 실패:", e)

# 알림 로그 기록 함수
def log_alert(profile_name):
    log_dir = os.path.join("logs", "alert")
    os.makedirs(log_dir, exist_ok=True)

    now = datetime.now()
    log_file = os.path.join(log_dir, f"{now:%Y-%m-%d}.log")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 프로필({profile_name}) 차량 감지 알림 발생\n")

# 알림 호출 함수
def trigger_alert(profile_name="default", volume=0.8, duration_sec=2.0):
    play_alert_sound(volume, duration_sec)
    log_alert(profile_name)

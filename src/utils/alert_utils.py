import os
import json
import time
import pygame
from datetime import datetime
import shutil

CONFIG_PATH = os.path.join("config", "alert_config.json")
SOUND_DIR = os.path.join("resources", "sounds")
ALERT_LOG_DIR = os.path.join("logs", "alert")

DEFAULT_SETTINGS = {
    "default": {
        "sound": "alert.mp3",
        "volume": 0.8,
        "duration": 2.0,
        "enabled": True
    }
}

def ensure_dirs():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    os.makedirs(SOUND_DIR, exist_ok=True)
    os.makedirs(ALERT_LOG_DIR, exist_ok=True)

def load_alert_config(profile_name="default"):
    ensure_dirs()
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get(profile_name, DEFAULT_SETTINGS["default"])

def save_alert_config(profile_name, config_data):
    ensure_dirs()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        all_config = json.load(f)
    all_config[profile_name] = config_data
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(all_config, f, indent=4)

def get_sound_list():
    ensure_dirs()
    return [f for f in os.listdir(SOUND_DIR) if f.lower().endswith((".mp3", ".wav"))]

def play_alert_sound(filename="alert.mp3", volume=0.8, duration=2.0):
    try:
        pygame.mixer.init()
        full_path = os.path.join(SOUND_DIR, filename)
        if not os.path.exists(full_path):
            print(f"❌ 알림음 파일 없음: {full_path}")
            return
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()
        time.sleep(duration)
        pygame.mixer.music.stop()
    except Exception as e:
        print(f"❌ 알림음 재생 실패: {e}")

def log_alert(profile_name):
    ensure_dirs()
    now = datetime.now()
    log_file = os.path.join(ALERT_LOG_DIR, f"{now:%Y-%m-%d}.log")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] 프로필({profile_name}) 차량 감지 알림 발생\n")

def trigger_alert(profile_name="default", sound="alert.mp3", volume=0.8, duration=2.0):
    play_alert_sound(sound, volume, duration)
    log_alert(profile_name)

def add_custom_sound(src_path):
    ensure_dirs()
    filename = os.path.basename(src_path)
    dest_path = os.path.join(SOUND_DIR, filename)
    if not os.path.exists(dest_path):
        shutil.copy(src_path, dest_path)
    return filename

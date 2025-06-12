# src/utils/alert_utils.py
import os
import json
import time
import pygame

CONFIG_PATH = os.path.join("config", "alert_config.json")
SOUND_DIR = os.path.join("resources", "sounds")

DEFAULT_SETTINGS = {
    "default": {
        "sound": "alert.mp3",
        "volume": 0.8,
        "duration": 2.0,
        "enabled": True
    }
}


def ensure_config():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)


def load_alert_config(profile_name="default"):
    ensure_config()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get(profile_name, DEFAULT_SETTINGS["default"])


def save_alert_config(profile_name, config_data):
    ensure_config()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        all_config = json.load(f)
    all_config[profile_name] = config_data
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(all_config, f, indent=4)


def get_sound_list():
    if not os.path.exists(SOUND_DIR):
        return []
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

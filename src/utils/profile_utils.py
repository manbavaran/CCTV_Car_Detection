import os
import json

# 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
PROFILES_DIR = os.path.join(BASE_DIR, "src", "profiles")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
MEDIA_DIR = os.path.join(BASE_DIR, "media")

PROFILES_LIST_FILE = os.path.join(CONFIG_DIR, "profiles.json")
DEFAULT_PROFILE_FILE = os.path.join(CONFIG_DIR, "default_profile.txt")

def ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def get_profiles():
    ensure_config_dir()
    if not os.path.exists(PROFILES_LIST_FILE):
        return []
    with open(PROFILES_LIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_profiles(profiles):
    ensure_config_dir()
    with open(PROFILES_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2, ensure_ascii=False)

def create_profile(profile_name, description=""):
    profiles = get_profiles()
    if any(p["name"] == profile_name for p in profiles):
        raise ValueError("이미 존재하는 프로필 이름입니다.")
    profiles.append({"name": profile_name, "description": description})
    save_profiles(profiles)

    # profile-specific directories
    os.makedirs(os.path.join(PROFILES_DIR, profile_name), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, profile_name), exist_ok=True)
    os.makedirs(os.path.join(MEDIA_DIR, profile_name), exist_ok=True)

def delete_profile(profile_name):
    profiles = get_profiles()
    profiles = [p for p in profiles if p["name"] != profile_name]
    save_profiles(profiles)
    # 주의: 실제 디렉토리 삭제는 안전 문제로 생략 (수동 삭제 권장)

def get_default_profile():
    if os.path.exists(DEFAULT_PROFILE_FILE):
        with open(DEFAULT_PROFILE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def set_default_profile(profile_name):
    profiles = get_profiles()
    if not any(p["name"] == profile_name for p in profiles):
        raise ValueError("존재하지 않는 프로필입니다.")
    with open(DEFAULT_PROFILE_FILE, "w", encoding="utf-8") as f:
        f.write(profile_name)

def get_profile_description(profile_name):
    profiles = get_profiles()
    for p in profiles:
        if p["name"] == profile_name:
            return p.get("description", "")
    return ""

def update_profile_description(profile_name, new_description):
    profiles = get_profiles()
    for p in profiles:
        if p["name"] == profile_name:
            p["description"] = new_description
            break
    save_profiles(profiles)

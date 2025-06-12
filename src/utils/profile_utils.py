import os
import json

CONFIG_DIR = "config"
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
    os.makedirs(f"src/profiles/{profile_name}", exist_ok=True)
    os.makedirs(f"logs/{profile_name}", exist_ok=True)
    os.makedirs(f"media/{profile_name}", exist_ok=True)

def delete_profile(profile_name):
    profiles = get_profiles()
    profiles = [p for p in profiles if p["name"] != profile_name]
    save_profiles(profiles)

    # NOTE: 실제 폴더 삭제는 위험할 수 있으므로 생략. 필요시 수동 삭제 권장

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

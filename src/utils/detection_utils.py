import os
import json

def get_detection_config_path(profile_name="default"):
    return os.path.join("config", f"detection_config_{profile_name}.json")

def load_detection_config(profile_name="default"):
    path = get_detection_config_path(profile_name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "sensitivity": 0.5,
            "fps": 8,
            "yolo_model": "yolov5n",
            "blob_min_area": 3000,
            "blob_max_area": None,
            "repeated_detection": 1,
            "cooldown_sec": 5
        }

def save_detection_config(config, profile_name="default"):
    path = get_detection_config_path(profile_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# 예시 사용 (개발 중 확인용)
if __name__ == "__main__":
    profile = "default"
    cfg = load_detection_config(profile)
    print("현재 설정:", cfg)

    # 테스트로 민감도 수정
    cfg["sensitivity"] = 0.7
    save_detection_config(cfg, profile)
    print("설정 저장 완료")

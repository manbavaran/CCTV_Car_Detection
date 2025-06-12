import os
import json

CONFIG_PATH = os.path.join("config", "model_config.json")
MODELS_DIR = os.path.join("models")

DEFAULT_CONFIG = {
    "selected_model": "yolov5n.pt"
}

def ensure_config():
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)

def get_model_list():
    """models 폴더 내 .pt 모델 리스트 반환"""
    if not os.path.exists(MODELS_DIR):
        return []
    return [f for f in os.listdir(MODELS_DIR) if f.endswith(".pt")]

def get_selected_model():
    """현재 선택된 모델 파일 이름 반환"""
    ensure_config()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("selected_model", DEFAULT_CONFIG["selected_model"])

def set_selected_model(model_name):
    """모델 선택값 저장"""
    ensure_config()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["selected_model"] = model_name
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_model_path():
    """선택된 모델의 전체 경로 반환"""
    return os.path.join(MODELS_DIR, get_selected_model())

# src/utils/logger_utils.py
import os
import logging
from datetime import datetime

BASE_LOG_DIR = "logs"


def ensure_log_dir(profile_name):
    profile_log_dir = os.path.join(BASE_LOG_DIR, profile_name)
    os.makedirs(profile_log_dir, exist_ok=True)
    return profile_log_dir


def get_log_path(profile_name):
    date_str = datetime.now().strftime("%Y%m%d")
    log_dir = ensure_log_dir(profile_name)
    return os.path.join(log_dir, f"{date_str}.log")


def get_logger(profile_name):
    log_path = get_log_path(profile_name)
    logger = logging.getLogger(f"vehicle_logger_{profile_name}")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def log_event(profile_name, message):
    logger = get_logger(profile_name)
    logger.info(message)

import os
import logging
from datetime import datetime

# 날짜별 로그 파일 생성
def setup_logger(name, level=logging.INFO):
    today = datetime.now().strftime("%Y-%m-%d")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{today}.log")

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)

    return logger

# 공통 이벤트 로깅 함수
event_logger = setup_logger("event_logger")

def log_event(level, message):
    if level == "INFO":
        event_logger.info(message)
    elif level == "WARNING":
        event_logger.warning(message)
    elif level == "ERROR":
        event_logger.error(message)
    elif level == "DEBUG":
        event_logger.debug(message)
    elif level == "ALERT":
        event_logger.critical(message)
    else:
        event_logger.info(message)  # 기본 INFO 처리

import os
import logging
from datetime import datetime

# 로그 디렉토리 및 파일 지정 (루트 기준 logs/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_file():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}.log")

# 로그 객체(싱글톤) 생성
_logger = None
def get_logger():
    global _logger
    if _logger is not None:
        return _logger

    log_file = get_log_file()
    logger = logging.getLogger("event_logger")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    _logger = logger
    return logger

def log_event(level, message):
    """
    level: "INFO", "WARNING", "ERROR", "ALERT", "DEBUG" 중 하나(대소문자 무관)
    message: 기록할 내용(문자열)
    """
    logger = get_logger()
    level = level.upper()
    if level == "INFO":
        logger.info(message)
    elif level == "WARNING":
        logger.warning(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "ALERT":
        logger.critical(message)
    elif level == "DEBUG":
        logger.debug(message)
    else:
        logger.info(message)  # 기본 INFO 처리

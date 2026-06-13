from logging.handlers import RotatingFileHandler
from pathlib import Path
import logging

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_logger(name="ai_social_media"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler = RotatingFileHandler(LOG_DIR / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


app_logger = get_logger()


def log_event(message, level="info", **extra):
    payload = f"{message} | {extra}" if extra else message
    getattr(app_logger, level.lower(), app_logger.info)(payload)
    return {"status": "logged", "level": level, "message": message}

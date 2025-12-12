import logging
from logging.handlers import RotatingFileHandler
import os
from flask import has_request_context, session

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "LakeraApplication.log")  # single log file

# -------------------------------
# Custom filter to inject session_id
# -------------------------------
class SessionFilter(logging.Filter):
    """
    Adds session_id from Flask session to every log record.
    """
    def filter(self, record):
        if has_request_context() and "session_id" in session:
            record.session_id = session["session_id"]
        else:
            record.session_id = "no-session"
        return True

def getlogger(name: str):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Single rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding="utf-8"
    )

    # Updated formatter to include session_id
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] [session=%(session_id)s] %(message)s"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(SessionFilter())  # attach filter
    logger.addHandler(file_handler)

    return logger

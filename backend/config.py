"""
Logger setup for the whole project
"""
import logging
import os

from logging.handlers import RotatingFileHandler

def setup_logger():
    """
    Sets up the logger for the backend application.
    Max size of the loggin file is 10 MB
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    # Całkiem spoko funkcjonalność, warto poczytać:
    # https://docs.python.org/3/library/logging.handlers.html

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "neurosphere_backend.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )

    console_handler = logging.StreamHandler()

    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

import logging
import sys
from pathlib import Path
from .config import LOGS_DIR

def setup_logger(name: str, log_file: str = "app.log", level=logging.INFO):
    """
    Sets up a logger with console and file handlers.
    """
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # File Handler
    file_handler = logging.FileHandler(LOGS_DIR / log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    # On Windows, we need to ensure utf-8 if we have emojis or non-ascii
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

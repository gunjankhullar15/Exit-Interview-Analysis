import logging
import os
from logging.handlers import RotatingFileHandler

def setup_custom_logger(name: str):
    """
    Creates and configures a customized logger that outputs to both 
    the terminal and a rotating text file.
    """
    # 1. Ensure the logs directory exists at the root of your project
    os.makedirs("logs", exist_ok=True)

    # 2. Define the visual format of the logs
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # 3. Set up the Rotating File Handler (Max 5MB per file, keep 3 backups)
    file_handler = RotatingFileHandler(
        "logs/exit_analysis.log", 
        maxBytes=5 * 1024 * 1024, 
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 4. Set up the Terminal/Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 5. Initialize the Logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 6. Prevent duplicate logs if this function is called multiple times
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
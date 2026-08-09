import logging
from .paths import log_path

RESET = "\033[0m"
COLORS = {
    logging.DEBUG: "\033[90m",
    logging.INFO: "\033[97m",
    logging.WARNING: "\033[93m",
    logging.ERROR: "\033[91m",
    logging.CRITICAL: "\033[91m",
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        plain = super().format(record)
        return f"{COLORS.get(record.levelno, '')}{plain}{RESET}"


def build_logger(headless: bool = False, level: str = "info") -> logging.Logger:
    logger = logging.getLogger("mousemover")
    logger.handlers.clear()
    logger.propagate = False

    numeric = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric)
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    file_handler = logging.FileHandler(log_path(), encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt, datefmt))
    file_handler.setLevel(numeric)
    logger.addHandler(file_handler)

    if not headless:
        console = logging.StreamHandler()
        console.setFormatter(ColorFormatter(fmt, datefmt))
        console.setLevel(numeric)
        logger.addHandler(console)

    return logger

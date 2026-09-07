import logging
from pathlib import Path


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "veilforge.log"


def get_logger(
    name: str = "veilforge",
) -> logging.Logger:
    """
    Create and return a configured VeilForge logger.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    file_handler.setLevel(
        logging.INFO
    )

    file_handler.setFormatter(
        formatter
    )

    console_handler = logging.StreamHandler()

    console_handler.setLevel(
        logging.WARNING
    )

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )

    logger.propagate = False

    return logger
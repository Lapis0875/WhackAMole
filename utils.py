from logging import Logger, DEBUG, INFO, WARNING, ERROR, CRITICAL
import logging
from sys import stdout


def createLogger(name: str, level: int, fmt: str) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(stdout)
    handler.setFormatter(
        logging.Formatter(
            style='{',
            fmt=fmt
        )
    )
    logger.addHandler(handler)
    return logger


def createStandardLogger(name: str, level: int) -> Logger:
    return createLogger(
        name,
        level,
        '[{asctime}] [{levelname}] {name} > {message}'
    )

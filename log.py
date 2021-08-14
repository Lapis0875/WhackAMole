import logging
import datetime
from sys import stdout
from logging import INFO, DEBUG, ERROR, CRITICAL

__all__ = (
    'kstnow',
    'init_logger',
    'INFO',
    'DEBUG',
    'ERROR',
    'CRITICAL'
)


def kstnow():
    """
    Get current datetime as kst.
    To reduce dependency, I just used datetime.timezone object.
    :return: datetime.datetime object with tzinfo = timezone('Asia/Seoul')
    """
    utcnow = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    return utcnow.astimezone(datetime.timezone(datetime.timedelta(hours=9), name='Asia/Seoul'))


def _get_log_file_name() -> str:
    """
    Get log file name using current kst datetime.
    :return: log file name ends with '.txt'
    """
    return f'{kstnow().isoformat(timespec="seconds").replace(":", "-")}.txt'


def init_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    stream_handler = logging.StreamHandler(stream=stdout)
    fmt = logging.Formatter(
        style='{',
        fmt='[{asctime}] [{levelname}] {name}: {message}'
    )
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler(f'./logs/{_get_log_file_name()}', encoding='utf-8')
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    return logger


def get_initialized_logger(name: str):
    logger = logging.getLogger(name)
    if len(logger.handlers) != 0:
        raise ValueError(f'Logger named {name} is not initialized!')
    elif len(logger.handlers) > 2:
        raise ValueError(f'Logger named {name} is malformed!')
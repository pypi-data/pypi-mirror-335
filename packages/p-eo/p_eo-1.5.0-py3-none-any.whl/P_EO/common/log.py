import logging
import os.path
import time
from pathlib import Path

from P_EO.common.config import LogConfig

__all__ = ['set_logger', 'LogMixin']

LOGGER_NAME = 'PEO'
LOGGER = logging.Logger(LOGGER_NAME)
LOGGER_INIT_FLAG = False

DEFAULT_LOG_FORMAT = "%(asctime)s-[%(filename)s:%(lineno)d]-[%(levelname)s]: %(message)s"
DEFAULT_LOG_PATH = Path(os.getcwd()).joinpath('peo_log', time.strftime("%Y%m%d"))
DEFAULT_LOG_NAME = f'peo_error.log'

# LOG 流设置
STREAM_LOG_FORMATTER = DEFAULT_LOG_FORMAT
STREAM_LOG_LEVEL = logging.INFO

# LOG FILE 设置
FILE_LOG_FORMATTER = DEFAULT_LOG_FORMAT
FILE_LOG_LEVEL = logging.INFO
FILE_LOG_PATH = DEFAULT_LOG_PATH
FILE_LOG_NAME = DEFAULT_LOG_NAME


def default_log() -> logging.Logger:
    if not LogConfig.init_default_logger:
        return LOGGER

    LOGGER.setLevel(logging.DEBUG)

    stream = logging.StreamHandler()
    _format = DEFAULT_LOG_FORMAT
    formatter = logging.Formatter(fmt=_format)
    stream.setFormatter(formatter)
    stream.setLevel(STREAM_LOG_LEVEL)
    LOGGER.addHandler(stream)

    FILE_LOG_PATH.mkdir(parents=True, exist_ok=True)
    file_path = FILE_LOG_PATH.joinpath(FILE_LOG_NAME)
    file = logging.FileHandler(file_path, encoding='utf-8')
    _format = DEFAULT_LOG_FORMAT
    formatter = logging.Formatter(fmt=_format)
    file.setFormatter(formatter)
    file.setLevel(FILE_LOG_LEVEL)
    LOGGER.addHandler(file)

    LOGGER.debug(f'当前logger: {LOGGER.name}, logger 初始化完成！')
    return LOGGER


def set_logger(logger: logging.Logger):
    if not isinstance(logger, logging.Logger):
        raise Exception(f'logger 类型不正确！{logger}')

    global LOGGER
    LOGGER = logger
    LOGGER.debug(f'更新logger: {logger.name}')


class LogMixin:
    @staticmethod
    def init_log():
        global LOGGER, LOGGER_NAME, LOGGER_INIT_FLAG
        if LOGGER.name == LOGGER_NAME and not LOGGER_INIT_FLAG:
            LOGGER = default_log()
            LOGGER_INIT_FLAG = True

    @property
    def log(self) -> logging.Logger:
        self.init_log()
        return LOGGER



import logging
from common import LOGGING_FORMAT

def LoggingFactory(name: str, level: int) -> logging.Logger:
    Logger = logging.getLogger(name)
    Logger.setLevel(level)
    StreamHandler = logging.StreamHandler()
    StreamHandler.setLevel(level)
    formatter = logging.Formatter(LOGGING_FORMAT)
    StreamHandler.setFormatter(formatter)
    Logger.addHandler(StreamHandler)
    return Logger
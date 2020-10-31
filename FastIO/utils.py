"""
Author
------
- Yuval Kaneti

Purpose
-------
- Utility Functions For FastIO.
"""

## Imports
import logging
from .common import LOGGING_FORMAT, LOGGING_LEVEL

## Functions
def LoggingFactory(name: str, level: int=LOGGING_LEVEL) -> logging.Logger:
    """LoggingFactory: A Logging asstince for FastIO.

    Parameters
    ----------
    name : str
        The Logger name.

    level : int, optional
        The Logging Level, by default LOGGING_LEVEL.

    Returns
    -------
    logging.Logger
        The Logger.
    """    
    Logger = logging.getLogger(name)
    Logger.setLevel(level)
    StreamHandler = logging.StreamHandler()
    StreamHandler.setLevel(level)
    formatter = logging.Formatter(LOGGING_FORMAT)
    StreamHandler.setFormatter(formatter)
    Logger.addHandler(StreamHandler)
    return Logger


"""
Author
------
- Yuval Kaneti.
Purpose
------
- An Asynchronouse shutil & os Like Module for Fast IO.
"""
__version__ = "1.0.2"
__all__ = ["walk", "CopyFile", "CopyFiles", "CopyDir", "CopyDirExecutor", "AsyncMap", "Logger", "LOGGING_LEVEL"]

from .utils import LoggingFactory
from .common import LOGGING_LEVEL
Logger = LoggingFactory(__name__, LOGGING_LEVEL)

from .miscellaneous import walk
from .files import CopyFile, CopyFiles
from .directories import CopyDir, CopyDirExecutor
from .preprocessing import AsyncMap

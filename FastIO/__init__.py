"""
Author
------
- Yuval Kaneti.
Purpose
------
- An Asynchronouse shutil & os Like Module for Fast IO.
"""
__version__ = "1.0.1"
__all__ = ["walk", "CopyFile", "CopyFiles", "CopyDir", "CopyDirExecutor"]

from .utils import LoggingFactory
from .common import LOGGING_LEVEL
Logger = LoggingFactory(__name__, LOGGING_LEVEL)

from .miscellaneous import walk
from .files import CopyFile, CopyFiles
from .directories import CopyDir, CopyDirExecutor

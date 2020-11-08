"""
Author
------
- Yuval Kaneti.
Purpose 
--------
- Constants & Common Variables For FastIO.
"""
## Imports
import logging
from typing import Union

DEBUG = True
MAX_WORKERS = 124
PAGE_SIZE = 4096
PYTHON_PAGE_COUNT = 64
BUFFER_SIZE = PYTHON_PAGE_COUNT * PAGE_SIZE # Not scientific.

READ_BYTES = "rb"
READ = 'r'
WRITE_BYTES = "wb"
WRITE = 'w'
READING_MODES = [READ_BYTES, READ]
WRITING_MODES = [WRITE_BYTES, WRITE]

STRING_OR_BYTES = Union[str, bytes]

HTTP_GET = 'GET'
HTTP_POST = 'POST'
HTTP_METHODS = [HTTP_GET, HTTP_POST]

LOGGING_FORMAT_DEBUG = "%(levelname)s - %(name)s - [%(filename)s:%(lineno)s] - %(asctime)s >> %(message)s"
LOGGING_FORMAT_PROD = "%(levelname)s - [%(filename)s:%(lineno)s] - %(asctime)s >> %(message)s"
LOGGING_FORMAT = LOGGING_FORMAT_DEBUG if DEBUG else LOGGING_FORMAT_PROD
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
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

DEBUG = True
PAGE_SIZE = 4096
PYTHON_PAGE_COUNT = 64
BUFFER_SIZE = PYTHON_PAGE_COUNT * PAGE_SIZE # Not scientific.
READ_BYTES = "rb"
WRITE_BYTES = "wb"
MAX_WORKERS = 124
LOGGING_FORMAT = '%(levelname)s - %(name)s - %(funcName)s - %(asctime)s - %(message)s'
LOGGING_LEVEL = logging.INFO if not DEBUG else logging.DEBUG
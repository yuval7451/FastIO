# Auhor: Yuval Kaneti

PAGE_SIZE = 4096
PYTHON_PAGE_COUNT = 32
BUFFER_SIZE = PYTHON_PAGE_COUNT * PAGE_SIZE # Not scientific.
READ_BYTES = "rb"
WRITE_BYTES = "wb"
MAX_WORKERS = 256
LOGGING_FORMAT = '%(levelname)s - %(name)s - %(funcName)s - %(asctime)s - %(message)s'
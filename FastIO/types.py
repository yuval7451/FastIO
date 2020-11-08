"""
Author
------
- Yuval Kaneti.

Purpose
-------
- Types for FastIO.
"""
import enum
from FastIO.miscellaneous import blocking_read, http_request, read

class FastIOAsyncFetchTypes(enum.Enum):
    FILE = read
    URL = http_request
    def __init__(self):
        raise RuntimeError("Do Not Create an instence of FastIOAsyncFetchTypes, use FastIOAsyncFetchTypes.FILE, FastIOAsyncFetchTypes.URL, etc.")  
    def __call__(self):
        raise RuntimeError("Do Not call an instence of FastIOAsyncFetchTypes, use FastIOAsyncFetchTypes.FILE, FastIOAsyncFetchTypes.URL, etc.")

class FastIOSyncFetchTypes(enum.Enum):
    FILE = blocking_read
    def __init__(self):
        raise RuntimeError("Do Not Create an instence of FastIOSyncFetchTypes, use FastIOSyncFetchTypes.FILE, etc.")  
    def __call__(self):
        raise RuntimeError("Do Not call an instence of FastIOSyncFetchTypes, use FastIOSyncFetchTypes.FILE, etc.")

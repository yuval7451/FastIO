"""
Author
------
- Yuval Kaneti.

Purpose
-------
- Asynchronouse Non-Blocking Functions & Coroutines for Miscellaneous IO.
"""
## Imports
import os
import aiofiles
import aiohttp

from contextlib import suppress

from typing import AsyncGenerator, Iterator, List, Tuple, Union

from FastIO import Logger
from FastIO.decorators import async_performance
from FastIO.common import BUFFER_SIZE, HTTP_GET, HTTP_METHODS, READING_MODES, DEBUG, READ_BYTES

## Functions
@async_performance
async def walk(top: str) -> AsyncGenerator[Tuple[str, List[str], List[str]], None]:
    """walk: AsyncGenerator Implementation of os.walk & os.scandir.

    Parameters
    ----------
    top : str
        The Current top Directory path.

    Returns
    -------
        AsyncGenerator[Tuple[str, List[str], List[str]], None]
            An AsyncGenerator That Yields iterators over the Directory.

    Yields
    -------
    Iterator[AsyncGenerator[Tuple[str, List[str], List[str]], None]]
        An Iterator Over the Current Directory State.
    -----
    ```
        async for (basedir, dirs, filenames) in FastIO.walk("YOUR\\SOURCE\\DIR"):
            print(basedir, dirs, filenames) 
    ```
    """
    Logger.info(f"Starting to walk {top}")
    top = os.fspath(top)
    dirs: List[str] = []
    files: List[str] = []

    with suppress(IOError):
        scandir_it: Iterator = os.scandir(top)
        with scandir_it:
            for entry in scandir_it:
                if entry.is_dir():
                    Logger.debug(f"Found Directory {entry.name}")
                    dirs.append(entry.name)
                else:
                    Logger.debug(f"Found File {entry.name}")
                    files.append(entry.name)

        # Yield before recursions.
        yield top, dirs, files

        # Recurse into sub-directories.
        Logger.debug("Starting to Recurse into sub-directories")
        for dirname in dirs:
            new_top = os.path.join(top, dirname)
            if not os.path.islink(new_top):
                async for (_top, _dirs, _filenames) in walk(top=new_top):
                    yield _top, _dirs, _filenames

async def read(file_name: str, mode: str=READ_BYTES, **kwargs) -> Union[bytes, str]:
    """read: A Wraper for aiofiles.open(...)

    Parameters
    ----------
    file_name : str
        The file name.

    mode : str
        The reading mode. 

    Awaits
    ------
    - Coroutine[AsyncBufferedReader.read()].

    Returns
    -------
    Union[bytes, str]
        The file Content in String | Bytes Depnding on the Reading mode
    """    
    assert mode in READING_MODES, 'Invalid mode: {} for Reading, VALID Modes are: {}'.format(mode, READING_MODES)
    buffer = b'' if mode=='rb' else ''
    with suppress(PermissionError, IOError):
        async with aiofiles.open(file=file_name, mode=mode) as fd:
            while True:
                chunk = await fd.read(BUFFER_SIZE) # type: ignore
                buffer += chunk
                if not chunk:
                    break
    return buffer
    
async def http_request(url: str, method: str=HTTP_GET, **kwargs):
    assert method in HTTP_METHODS, 'Invalid method: {} for HTTP Request, VALID Nethods are: {}'.format(method, HTTP_METHODS)
    async with aiohttp.request(method=method, url=url) as response:
        return await response.text()

def blocking_read(file_name: str, mode: str=READ_BYTES, **kwargs):
    assert mode in READING_MODES, 'Invalid mode: {} for Reading, VALID Modes are: {}'.format(mode, READING_MODES)
    buffer = b'' if mode=='rb' else ''
    with suppress(PermissionError, IOError):
        with open(file_name, mode) as fd:
            while True:
                chunk = fd.read(BUFFER_SIZE)
                buffer += chunk
                if not chunk:
                    break
    return buffer

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
from contextlib import suppress
from typing import AsyncGenerator, Iterator, List, Tuple

from FastIO import Logger

## Functions
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


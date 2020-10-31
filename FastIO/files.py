"""
Author 
------
- Yuval Kaneti.
Purpose
-------
- Asynchronouse Non-Blocking Functions & Coroutines for File IO. 
"""

## Imports
import os
import tqdm
from contextlib import suppress

import asyncio
import aiofiles

from aiofiles.threadpool.binary import AsyncBufferedReader, AsyncBufferedIOBase
from asyncio import Semaphore

from FastIO import Logger
from FastIO.common import MAX_WORKERS, READ_BYTES, WRITE_BYTES, BUFFER_SIZE

## Functions
async def CopyFiles(src: str, dst: str, max_workers: int=MAX_WORKERS) -> None:
    """CopyFiles A Faster shutil.CopyFiles Implementation.

    Parameters
    ----------
    src : str
        The source dir path.

    dst : str
        The destention dir path.

    max_workers : int, optional
        The Number of concurrent Coroutines, by default MAX_WORKERS.
    
    Awaits
    ------
    - List[Coroutine[_CopyFile(...)]].
    
    Notes
    -----
    - A Faster Asynchronouse shutil.copydir Implementation.
    - Will Only Copy Files from src -> dst.
    - Directory Structure will not be mirrored, use FastIO.CopyDir(...) instead.
    
    Usage
    -----
    ```
        await CopyFiles("YOUR\\SOURCE\\DIR", "YOUR\\DESTINATION\\DIR")
    ```
    """    
    Logger.info(f"Starting to Copy Files from {src} -> {dst}")
    Logger.info(f"Runnning {max_workers} Coroutines concurrently")
    futures = []

    # Supress Errors if the directory Already Exists.
    with suppress(FileExistsError):
        if not os.path.exists(dst):
            os.makedirs(dst)
            Logger.debug(f"Creating {dst} Directory because it did not exists")

    entries  = os.listdir(src)
    total_entries = len(entries )
    semaphore = Semaphore(max_workers)
    Logger.debug(f"Starting to go over {total_entries} entries")
    with tqdm.tqdm(total=total_entries) as pbar:
        for entry in entries:
            src_file = os.path.join(src, entry)
            if os.path.isfile(src_file):
                dst_file = os.path.join(dst, entry)
                futures.append(_CopyFile(src_file=src_file, dst_file=dst_file, semaphore=semaphore, pbar=pbar))

        await asyncio.gather(*futures)

async def CopyFile(src_file: str, dst_file: str) -> None:
    """CopyFile Asynchronouse shutil.copy Implementation.

    Parameters
    ----------
    src_file : str
        The source file path.

    dst_file : str
        The destention file path.

    Awaits
    ------
    - Coroutine[CopyFileObj()].

    Notes
    -----
    - Asynchronouse shutil.copy Implementation.

    Usage
    -----
    ```
        await FastIO.CopyFile("YOUR\\SOURCE\\FILE", "YOUR\\DESTINATION\\FILE")
    ```
    """    
    async with aiofiles.open(src_file, mode=READ_BYTES) as src_fd:
        async with aiofiles.open(dst_file, mode=WRITE_BYTES) as dst_fd:
            await _CopyFileObj(src_fd=src_fd, dst_fd=dst_fd)
                        
async def _CopyFile(src_file: str, dst_file: str, semaphore: asyncio.Semaphore, pbar: tqdm.std.tqdm=None) -> None:
    """_CopyFile Asynchronouse shutil.copy Implementation.

    Parameters
    ----------
    src_file : str
        The source file path.

    dst_file : str
        The destention file path.
    
    semaphore : asyncio.Semaphore
        A semaphore To Limit concourant call to _CopyFileObj(...)
    
    pbar : tqdm.std.tqdm, optional
        The Progress bar of the event loop, by default None
    
    Awaits
    ------
    - Coroutine[CopyFileObj()].
    
    Notes
    -----
    - Asynchronouse shutil.copy Implementation.
    - Used By FastIO.CopyDir & FastIO.CopyFiles for Progress bar & Synchronization Primitives (semaphore).
    - Should not be used directly, Use FastIO.CopyFile(...), FastIO.CopyFiles(...), FastIO.CopyDir(...) instead.
    """              
    async with semaphore:
        async with aiofiles.open(src_file, mode=READ_BYTES) as src_fd:
            async with aiofiles.open(dst_file, mode=WRITE_BYTES) as dst_fd:
                await _CopyFileObj(src_fd=src_fd, dst_fd=dst_fd)
                if pbar is not None:
                    pbar.update(1)

async def _CopyFileObj(src_fd: AsyncBufferedReader, dst_fd: AsyncBufferedIOBase) -> None:
    """_CopyFileObj Copy Data from File Descriptor to Another.

    Parameters
    ----------
    src_fd : AsyncBufferedReader
         A File Descriptor Like object.

    dst_fd : AsyncBufferedIOBase
         A File Descriptor Like object.

    Awaits
    ------
    - Coroutine[AsyncBufferedReader.read(), AsyncBufferedIOBase.write()].

    Notes
    -----
    - Copy Data from file-like Object src_fd to file-like Object dst_fd.
    - Async shutil.copy Implementation.
    - Should not be used directly, Use FastIO.CopyFile(...) instead.
    """    
    while True:
        buffer = await src_fd.read(BUFFER_SIZE) # type: ignore
        if not buffer:
            break
        await dst_fd.write(buffer) # type: ignore

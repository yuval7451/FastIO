"""
Author
------
- Yuval Kaneti.
Purpose
-------
- Asynchronouse Non-Blocking Functions & Coroutines for Directory IO.
"""
## Imports
import os
import tqdm
from functools import partial
from contextlib import suppress

import asyncio
import concurrent.futures
from asyncio import Semaphore
from asyncio.events import AbstractEventLoop

from FastIO.common import MAX_WORKERS
from FastIO.miscellaneous import walk
from FastIO.files import CopyFile, _CopyFile
from FastIO import Logger

## Functions
async def CopyDirExecutor(src: str, dst: str, max_workers: int=MAX_WORKERS, loop: AbstractEventLoop=None) -> None:    
    """CopyDirExecutor: An Asynchronouse Executor Implementation for shutil.copydir.

    Parameters
    ----------
    src : str
        The source dir path.

    dst : str
        The destination dir path.

    max_workers : int, optional
       The Number of concurrent Executor Threads, by default MAX_WORKERS.

    loop : AbstractEventLoop, optional
        The Current Event loop, by default None.
    
    Awaits
    -----
    - List[Coroutine[AbstractEventLoop.run_in_executor(_CopyFileExecutor(...))]].

    Usage
    -----
    ```
        await CopyDirExecutor("YOUR\\SOURCE\\DIR", "YOUR\\DESTINATION\\DIR")
    ```
    """    
    Logger.info(f"Starting to Copy Files from {src} -> {dst}")
    if loop is None:
        Logger.debug(f"Initializing Loop")
        # Get The Current Runnning Loop
        loop = asyncio.get_running_loop()

    Logger.info(f"Runnning {max_workers} Coroutines concurrently")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        async for (basedir, dirs, filenames) in walk(src):
            for batch_idx in range(0, len(filenames), max_workers):
                if (batch_idx + max_workers) > len(filenames):
                    _filenames = filenames[batch_idx:]
                else:
                    _filenames = filenames[batch_idx:batch_idx+max_workers]
                
                with tqdm.tqdm(total=len(_filenames)) as pbar:
                    # TODO: Create a normal for loop instead for List Comp.
                    futures = [
                            loop.run_in_executor(
                                executor,
                                partial(
                                    _CopyFileExecutor,
                                    src_file=os.path.join(basedir, filename),
                                    dst_file=os.path.join(dst, filename),
                                    pbar=pbar
                                )
                            )
                            for filename in _filenames]
                            
                    await asyncio.gather(*futures)

def _CopyFileExecutor(src_file: str, dst_file: str, pbar: tqdm.std.tqdm) -> None:
    """_CopyFileExecutor: A Blocking Function the will be run inside a ThreadPoolExecutor.

    Parameters
    ----------
    src_file : str
        The Souce Path of the file.

    dst_file : str
        the destination path of the file.

    pbar : tqdm.std.tqdm
        The Progress bar of the main Thread.

    Notes
    -----
    - Run a coroutine in an Executor in a diffrent Thread Asynchronously.
    - Should not be used directly, Use FastIO.CopyDirExecutor(...), FastIO.CopyDir(...) instead.
    """    
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        file_parent = os.path.dirname(dst_file)    
        with suppress(FileExistsError):
            if not os.path.exists(file_parent):
                os.makedirs(file_parent)
        
        loop.run_until_complete(CopyFile(src_file=src_file, dst_file=dst_file))

    except:
        Logger.error("Error While Copying File", exc_info=True)

    finally:
        pbar.update(1)
        loop.close()

async def CopyDir(src: str, dst: str, max_workers: int=MAX_WORKERS) -> None:
    """CopyDir: A Faster Asynchronouse shutil.copydir Implementation.

    Parameters
    ----------
    src : str
        The Source dir path.
    
    dst : str
        The destination dir path.
    
    max_workers : int, optional
       The Number of concurrent Executor Threads, by default MAX_WORKERS.
    
    Awaits
    -----
    - List[Coroutine[_CopyFile(...)]], List[Coroutine[_CopyDir(...)]].

    Notes
    -----
    - A Faster Asynchronouse shutil.copydir Implementation.
    - Recursively Copfy Files and Mirror Directory structure.
    
    Usage
    -----
    ```
        await CopyDir("YOUR\\SOURCE\\DIR", "YOUR\\DESTINATION\\DIR")
    ```
    """        
    Logger.info(f"Starting to Copy Files from {src} -> {dst}")
    Logger.info(f"Runnning {max_workers} Coroutines concurrently")

    futures = []
    dirs = []
    # Supress Errors if the directory Already Exists.
    with suppress(FileExistsError):
        if not os.path.exists(dst):
            os.makedirs(dst)
    
    entrys = os.listdir(src)
    semaphore = Semaphore(max_workers)
    with tqdm.tqdm() as pbar:
        for entry in entrys:
            entry_path = os.path.join(src, entry)
            if os.path.isfile(entry_path):
                dst_file = os.path.join(dst, entry)
                futures.append(_CopyFile(src_file=entry_path, dst_file=dst_file, semaphore=semaphore, pbar=pbar))
            if os.path.isdir(entry_path):
                dirs.append(entry_path)
        
        await asyncio.gather(*futures)

        # Call _CopyDir which is basicly the same but without recursive Progress bar.
        dir_futures = []
        for dirname in dirs:
            dst_dir = os.path.join(dst, os.path.basename(dirname))
            dir_futures.append(_CopyDir(src=dirname, dst=dst_dir, semaphore=semaphore, pbar=pbar))


        await asyncio.gather(*dir_futures)

async def _CopyDir(src: str, dst: str, semaphore: asyncio.Semaphore, pbar: tqdm.std.tqdm) -> None:
    """_CopyDir: A Non Blocking Asynchronouse Recursive Coroutine That Copy Files.

    Parameters
    ----------
    src : str
        The Source dir path.

    dst : str
        The destination dir path.
    
    semaphore : asyncio.Semaphore
        A semaphore To Limit concourant call to _CopyFileObj(...).
    
    pbar : tqdm.std.tqdm
        The Progress bar of the event loop.

    Awaits
    ------
    - List[Coroutine[_CopyFile(...)]].

    Notes
    -----
    - Should not be used directly, Use FastIO.CopyDir(...) instead.
    - A Faster Asynchronouse shutil.copydir Implementation.
    - Recursively Copy Files and mirror directory Structure.
    """    
    futures = []
    dirs = []
    with suppress(FileExistsError):
        if not os.path.exists(dst):
            os.makedirs(dst)
    entrys = os.listdir(src)
    if semaphore is None:
       semaphore = Semaphore(MAX_WORKERS)
    for entry in entrys:
        entry_path = os.path.join(src, entry)
        if os.path.isfile(entry_path):
            dst_file = os.path.join(dst, entry)
            futures.append(_CopyFile(src_file=entry_path, dst_file=dst_file, semaphore=semaphore, pbar=pbar))
        if os.path.isdir(entry_path):
            dirs.append(entry_path)
    
    await asyncio.gather(*futures)

    dir_futures = []
    for dirname in dirs:
        dst_dir = os.path.join(dst, os.path.basename(dirname))
        dir_futures.append(_CopyDir(src=dirname, dst=dst_dir, semaphore=semaphore, pbar=pbar))

    await asyncio.gather(*dir_futures)


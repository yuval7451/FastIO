# Auhor: Yuval Kaneti
# An Asynchronouse shutil & os Like Module for Fast File IO

## Imports
import os
import tqdm
import logging
import asyncio
import aiofiles
import concurrent.futures
from functools import partial
from contextlib import suppress
from utils import LoggingFactory
from asyncio.events import AbstractEventLoop
from typing import AsyncGenerator, Iterator, List, Optional, Tuple
from common import MAX_WORKERS, READ_BYTES, WRITE_BYTES, BUFFER_SIZE
from aiofiles.threadpool.binary import AsyncBufferedReader, AsyncBufferedIOBase

## Logging
Logger = LoggingFactory(__name__, logging.INFO)

## Functions
async def walk(top: str) -> AsyncGenerator[Tuple[str, List[str], List[str]], None]:
    """
    @param top: C{str} -> The current top folder path.
    @yields: C{AsyncGenerator} -> A AsyncGenerator[Tuple[str, List[str], List[str]], None].
    @remarks:
             * AsyncGenerator Implementation of os.walk & os.scandir. 
    @usage:
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
                async for (_top, _dirs, _filenames) in walk(new_top):
                    yield _top, _dirs, _filenames

async def CopyDir(src: str, dst: str, max_workers: Optional[int]=MAX_WORKERS, loop: Optional[AbstractEventLoop]=None) -> None:
    """
    @param src: C{str} -> The source dir path.
    @param dst: C{str} -> The destention dir path.
    @param max_workers: C{int} -> The Number of concurrent Threads.
    @param loop: C{str} -> The Current Event loop or None. 
    @awaits: Tuple[Coroutine[AbstractEventLoop.run_in_executor(_CopyFileWraper(...))]].
    @remarks: 
             * Asynchronouse shutil.copydir Implementation.
    @usage:
        ```
            await CopyDir("YOUR\\SOURCE\\DIR", "YOUR\\DESTINATION\\DIR")
        ```
    """
    Logger.info(f"Starting to Copy Files from {src} -> {dst}")
    if loop is None:
        Logger.debug(f"Initializing Loop")
        # Get The Current Loop
        loop = asyncio.get_running_loop()

    Logger.debug("Initializing Executor with {max_workers} Threads")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # for Every File in the Current Directory,
        # Copy All The files Recursivly.
        async for (basedir, dirs, filenames) in walk(src):
            if max_workers < len(filenames):
                Logger.info(f"Runnning {max_workers} Coroutines concurrently Out of {len(filenames)} Coroutines")
            else:
                Logger.info(f"Runnning {len(filenames)} Coroutines concurrently")
            with tqdm.tqdm(total=len(filenames)) as pbar:
                futures = [
                        loop.run_in_executor(
                            executor,
                            partial(
                                _CopyFileWraper,
                                src_file=os.path.join(basedir, filename),
                                dst_file=os.path.join(dst, filename),
                                pbar=pbar
                            )
                        )
                        for filename in filenames]
                        
                await asyncio.gather(*futures)
                
async def CopyFile(src_file: str, dst_file: str) -> None:
    """
    @param src_file: C{str} -> the source file path.
    @param dst_file: C{str} -> the destention file path.
    @awaits Coroutine[CopyFileObj()].
    @remarks: 
             * Asynchronouse shutil.copy Implementation.
    @usage:
        ```
            await FastIO.CopyFile("YOUR\\SOURCE\\FILE", "YOUR\\DESTINATION\\FILE")
        ```
    """
    Logger.debug(f"Copying {src_file} -> {dst_file}")
    async with aiofiles.open(src_file, mode=READ_BYTES) as fd_src:
        async with aiofiles.open(dst_file, mode=WRITE_BYTES) as fd_dst:
            await _CopyFileObj(fd_src, fd_dst)
                        
async def _CopyFileObj(src_fd: AsyncBufferedReader, dst_fd: AsyncBufferedIOBase) -> None:
    """
    @param src_fd: C{AsyncBufferedReader} -> A File Descriptor Like object.
    @param dst_fd: C{AsyncBufferedIOBase} -> A File Descriptor Like object.
    @awaits: Coroutine[AsyncBufferedReader.read(), AsyncBufferedIOBase.write()].
    @remarks:
             * copy data from file-like object src_fd to file-like object dst_fd.
             * Async shutil.copy Implementation.
             ! Should not be used directly, Use FastIO.CopyFile(...) instead.
    """
    while True:
        buffer = await src_fd.read(BUFFER_SIZE) # type: ignore
        if not buffer:
            break
        await dst_fd.write(buffer) # type: ignore

def _CopyFileWraper(src_file: str, dst_file: str, pbar: tqdm.std.tqdm) -> None:
    """
    @param src_file: C{str} -> The source path of the file.
    @param dst_file: C{str} -> The destention path of the file.
    @param pbar: C{tqdm.std.tqdm} -> The Progress bar of the event loop
    @remarks:
             * Run a coroutine in an Executor in a diffrent Thread asynchronously .
             ! Should not be used directly, Use FastIO.CopyDir(...) instead.
    """
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        file_parent = os.path.dirname(dst_file)    
        with suppress(FileExistsError):
            if not os.path.exists(file_parent):
                os.makedirs(file_parent)
        
        loop.run_until_complete(CopyFile(src_file, dst_file))

    except:
        Logger.error("Error While Copying File", exc_info=True)

    finally:
        pbar.update(1)
        loop.close()

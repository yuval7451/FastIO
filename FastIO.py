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
from asyncio import Semaphore
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
                async for (_top, _dirs, _filenames) in walk(top=new_top):
                    yield _top, _dirs, _filenames

async def CopyDirExecutor(src: str, dst: str, max_workers: Optional[int]=MAX_WORKERS, loop: Optional[AbstractEventLoop]=None) -> None:
    """
    @param src: C{str} -> The source dir path.
    @param dst: C{str} -> The destention dir path.
    @param max_workers: C{int} -> The Number of concurrent Threads.
    @param loop: C{str} -> The Current Event loop or None. 
    @awaits: List[Coroutine[AbstractEventLoop.run_in_executor(_CopyFileExecutor(...))]].
    @remarks: 
             * Asynchronouse Executor shutil.copydir Implementation.
             * Recursively Copy Files and mirror directory Structure.
    @usage:
        ```
            await CopyDirExecutor("YOUR\\SOURCE\\DIR", "YOUR\\DESTINATION\\DIR", max_workers=64, loop=asyncio.get_running_loop())
        ```
    """
    Logger.info(f"Starting to Copy Files from {src} -> {dst}")
    if loop is None:
        Logger.debug(f"Initializing Loop")
        # Get The Current Loop
        loop = asyncio.get_running_loop()

    Logger.info(f"Runnning {max_workers} Coroutines concurrently")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        async for (basedir, dirs, filenames) in walk(src):
            for batch_idx in range(0, len(filenames), max_workers): # type: ignore
                if (batch_idx + max_workers) > len(filenames): # type: ignore
                    _filenames = filenames[batch_idx:]
                else:
                    _filenames = filenames[batch_idx:batch_idx+max_workers] # type: ignore
                
                with tqdm.tqdm(total=len(_filenames)) as pbar:
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
    """
    @param src_file: C{str} -> The source path of the file.
    @param dst_file: C{str} -> The destention path of the file.
    @param pbar: C{tqdm.std.tqdm} -> The Progress bar of the event loop
    @remarks:
             * Run a coroutine in an Executor in a diffrent Thread Asynchronously.
             ! Should not be used directly, Use FastIO.CopyDirExecutor(...), FastIO.CopyDir(...) instead.
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

async def CopyDir(src: str, dst: str) -> None:
    """
    @param src: C{str} -> The source dir path.
    @param dst: C{str} -> The destention dir path.
    @awaits: List[Coroutine[_CopyFile(...)]], List[Coroutine[_CopyDir(...)]].
    @remarks: 
             * A Faster Asynchronouse shutil.copydir Implementation.
             * Recursively Copy Files and mirror directory Structure.
    @usage:
        ```
            await CopyDir("YOUR\\SOURCE\\DIR", "YOUR\\DESTINATION\\DIR")
        ```
    """
    futures = []
    dirs = []
    with suppress(FileExistsError):
        if not os.path.exists(dst):
            os.makedirs(dst)
    entrys = os.listdir(src)
    semaphore = Semaphore(MAX_WORKERS)
    with tqdm.tqdm() as pbar:
        for entry in entrys:
            entry_path = os.path.join(src, entry)
            if os.path.isfile(entry_path):
                dst_file = os.path.join(dst, entry)
                futures.append(_CopyFile(src_file=entry_path, dst_file=dst_file, semaphore=semaphore, pbar=pbar))
            if os.path.isdir(entry_path):
                dirs.append(entry_path)
        
        await asyncio.gather(*futures)

    # NOTE: Using asyncio.gather should be faster altough there are some race conditions between the Tasks.
    # TODO: Try to Fix race condition using asyincio.Queue?, somehow fix tqdm bar.
        dir_futures = []
        for dirname in dirs:
            dst_dir = os.path.join(dst, os.path.basename(dirname))
            # dir_futures.append(CopyDir(dirname, dst_dir))
            dir_futures.append(_CopyDir(src=dirname, dst=dst_dir, semaphore=semaphore, pbar=pbar))


        await asyncio.gather(*dir_futures)

async def _CopyDir(src: str, dst: str, semaphore: asyncio.Semaphore, pbar: tqdm.std.tqdm) -> None:
    """
    @param src: C{str} -> The source dir path.
    @param dst: C{str} -> The destention dir path.
    @param pbar: C{tqdm.std.tqdm} -> The Progress bar of the event loop
    @param semaphore: C{asyncio.semaphore} -> A semaphore To Limit concourant call to _CopyFileObj(...)
    @awaits: List[Coroutine[_CopyFile(...)]].
    @remarks: 
             * A Faster Asynchronouse shutil.copydir Implementation.
             * Recursively Copy Files and mirror directory Structure.
    @usage:
        ```
            await CopyDir("YOUR\\SOURCE\\DIR", "YOUR\\DESTINATION\\DIR")
        ```
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

    # NOTE: Using asyncio.gather should be faster altough there are some race conditions between the Tasks.
    # TODO: Try to Fix race condition using asyincio.Queue?, somehow fix tqdm bar.
    dir_futures = []
    for dirname in dirs:
        dst_dir = os.path.join(dst, os.path.basename(dirname))
        # dir_futures.append(CopyDir(dirname, dst_dir))
        dir_futures.append(_CopyDir(src=dirname, dst=dst_dir, semaphore=semaphore, pbar=pbar))


    await asyncio.gather(*dir_futures)

    # NOTE: What should i do with this?
    # for dirname in dirs:
    #     dst_dir = os.path.join(dst, os.path.basename(dirname))
    #     await (CopyDir(dirname, dst_dir))

async def CopyFiles(src: str, dst: str) -> None:
    """
    @param src: C{str} -> The source dir path.
    @param dst: C{str} -> The destention dir path.
    @awaits: List[Coroutine[_CopyFile(...)]].
    @remarks: 
             * A Faster Asynchronouse shutil.copydir Implementation.
             * Will Only Copy Files from src -> dst.
             * directory Structure will not be mirrored, use FastIO.CopyDir(...) instead.
    @usage:
        ```
            await CopyFiles("YOUR\\SOURCE\\DIR", "YOUR\\DESTINATION\\DIR")
        ```
    """
    futures = []
    with suppress(FileExistsError):
        if not os.path.exists(dst):
            os.makedirs(dst)
    entrys = os.listdir(src)
    semaphore = Semaphore(MAX_WORKERS)
    with tqdm.tqdm(total=len(entrys)) as pbar:
        for entry in entrys:
            src_file = os.path.join(src, entry)
            if os.path.isfile(src_file):
                dst_file = os.path.join(dst, entry)
                futures.append(_CopyFile(src_file=src_file, dst_file=dst_file, semaphore=semaphore, pbar=pbar))

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
    async with aiofiles.open(src_file, mode=READ_BYTES) as src_fd:
        async with aiofiles.open(dst_file, mode=WRITE_BYTES) as dst_fd:
            await _CopyFileObj(src_fd=src_fd, dst_fd=dst_fd)
                        
async def _CopyFile(src_file: str, dst_file: str, semaphore: asyncio.Semaphore, pbar: Optional[tqdm.std.tqdm]=None) -> None:
    """
    @param src_file: C{str} -> the source file path.
    @param dst_file: C{str} -> the destention file path.
    @param semaphore: C{asyncio.semaphore} -> A semaphore To Limit concourant call to _CopyFileObj(...)
    @param pbar: C{tqdm.std.tqdm} -> The Progress bar of the event loop
    @awaits Coroutine[CopyFileObj()].
    @remarks: 
             * Asynchronouse shutil.copy Implementation.
             * Used By FastIO.CopyDir & FastIO.CopyFiles for Progress bar & Synchronization Primitives (semaphore).
             ! Should not be used directly, Use FastIO.CopyFile(...), FastIO.CopyFiles(...), FastIO.CopyDir(...) instead.

    """
    async with semaphore:
        Logger.debug(f"Copying {src_file} -> {dst_file}")
        async with aiofiles.open(src_file, mode=READ_BYTES) as src_fd:
            async with aiofiles.open(dst_file, mode=WRITE_BYTES) as dst_fd:
                await _CopyFileObj(src_fd=src_fd, dst_fd=dst_fd)
                if pbar is not None:
                    pbar.update(1)

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

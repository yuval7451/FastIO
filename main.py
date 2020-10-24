# Auhor: Yuval Kaneti

## Imports
import os
import aiofiles
import asyncio
import argparse
from tqdm import tqdm
from typing import AsyncGenerator, Iterator, List, Tuple, Coroutine
from aiofiles.threadpool.text import AsyncTextIOWrapper

class FastIO(object):
    """FastIO -> A Module for Fast File IO. """
    def __init__(self, src: str, dst: str):
        """
        @param src: C{str} -> The source Folder or File.
        @param dst: C{str} -> The destention Folder.
        """
        self.src = src
        self.dst = dst
        self.buffer = 16*1024
        self.read = "rb"
        self.write = "wb"
        self.semaphore: asyncio.Semaphore

    async def walk(self, top: str) -> AsyncGenerator[Tuple[str, List[str]], None]:
        """
        @param top: C{str} -> The current top folder path
        @yields: C{AsyncGenerator} -> A AsyncGenerator[Tuple[str, List[str]], None]
        @remarks:
                 * AsyncGenerator Implementation of os.walk & os.scandir. 
        """
        top = os.fspath(top)
        dirs: List[str] = []
        files: List[str] = []

        scandir_it: Iterator = os.scandir(top)
        with scandir_it:
            for entry in scandir_it:
                if entry.is_dir():
                    dirs.append(entry.name)
                else:
                    files.append(entry.name)

        # Yield before recursions
        yield top, files

        # Recurse into sub-directories
        for dirname in dirs:
            new_path = os.path.join(top, dirname)
            if not os.path.islink(new_path):
                async for (basedir, filenames) in self.walk(new_path):
                    yield basedir, filenames

    async def CopyDir(self):
        """
        @awaits: Coroutine[self.EnsureDirFuture()]
        @remarks: 
                 * Will mirror a directory structure.
                 * Use asyincio.gather if progress bar is redundant.
        """
        with tqdm(total=1000) as bar:
            async for (basedir, filenames) in self.walk(self.src):
                    # NOTE: IF Progress bar is redundant use asynio.gather instead.
                    # await asyncio.gather( *[self.EnsureDirFuture(
                    #                     os.path.join(basedir, filename), 
                    #                     os.path.join(self.dst, filename)) 
                    #                     for filename in filenames])

                for coro in asyncio.as_completed([self.EnsureDirFuture(os.path.join(basedir, filename), os.path.join(self.dst, filename)) for filename in filenames]):
                        await coro
                        bar.update(1)
                        
    async def CopyFileObj(self, fd_src: AsyncTextIOWrapper, fd_dst: AsyncTextIOWrapper):
        """
        @param fd_src: C{AsyncTextIOWrapper} -> A File Descriptor Like object
        @param fd_dst: C{AsyncTextIOWrapper} -> A File Descriptor Like object
        @awaits: Coroutine[AsyncTextIOWrapper.read(), AsyncTextIOWrapper.write()]
        @remarks:
                 * copy data from file-like object fd_src to file-like object fd_dst
                 * Async shutil.copy Implementation
        """
        while 1:
            buf = await fd_src.read(self.buffer) # type: ignore
            if not buf:
                break
            await fd_dst.write(buf) # type: ignore

    async def CopyFile(self, src_file: str, dst_file: str):
        """
        @param src_file: C{str} -> the source file path
        @param dst_file: C{str} -> the destention file path
        @awaits Coroutine[self.CopyFileObj()]
        @remarks: 
                 * Async shutil.copy Implementation

        """
        async with aiofiles.open(src_file, mode=self.read) as fd_src:
            async with aiofiles.open(dst_file, mode=self.write) as fd_dst:
                await self.CopyFileObj(fd_src, fd_dst)
  
    async def EnsureDirFuture(self, src_file: str, dst_file: str):
        """
        @param src_file: C{str} -> the source path of the file
        @param dst_file: C{str} -> the destention path of the file
        @awaits: Coroutine[self.CopyFile()]
        @remarks:
                 * Mirros the folder Structher to unsure safe Copying
        """
        async with self.semaphore:
            file_parent = os.path.dirname(dst_file)
            if not os.path.exists(file_parent):
                os.makedirs(file_parent)
            
            await self.CopyFile(src_file, dst_file)

    async def run(self):
        """
        @awaits: Coroutine[self.CopyDir(), self.CopyFile()]
        """
        self.semaphore = asyncio.Semaphore(50)
        if os.path.isdir(self.src):
            await self.CopyDir()
        elif  os.path.isfile(self.src):
            await self.CopyFile(self.src, self.dst)
        else:
            raise RuntimeError("Invalid source & destention paths")

if __name__ == "__main__":
    main_parser = argparse.ArgumentParser(prog='main.py')
    main_parser.add_argument('-s','--src', action='store', type=str,
                        required=True, help="the source", dest='src')

    main_parser.add_argument('-d','--dst', action='store', type=str,
                        required=True, help="The dest", dest='dst')

    args = main_parser.parse_args()

    asyncio.run(FastIO(args.src, args.dst).run())

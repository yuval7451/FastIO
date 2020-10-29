# Author: Yuval Kaneti
# Walk your entire Filesystem

import asyncio
from FastIO import walk
async def main():
   async for basedir, dirs, filenames in walk(r"C:\\"):
       print(basedir, dirs, filenames)

asyncio.run(main())
# Author: Yuval Kaneti

import time
import asyncio
from FastIO import CopyDir, Logger

async def main():
    start = time.time()
    await CopyDir(r"C:\Python27", r"D:\FastIO\Python27")
    end = time.time() - start
    Logger.info("it took {} Seconds".format(end))
asyncio.run(main())
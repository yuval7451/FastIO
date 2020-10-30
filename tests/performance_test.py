# Author: Yuval Kaneti

import time
import asyncio
from FastIO import CopyDir, Logger

async def main():
    start = time.time()
    await CopyDir(r"D:\FastIO\1GB\src", r"D:\FastIO\1GB\dst")
    end = time.time() - start
    Logger.info("it took {} Seconds".format(end))
asyncio.run(main())
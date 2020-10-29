# Author: Yuval Kaneti
# Backup your C Drive

import asyncio
from FastIO import CopyDir

async def main():
    await CopyDir(r"C:\\", r"D\\backup")

asyncio.run(main())
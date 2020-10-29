# Author: Yuval Kaneti
# Backup your C Drive

import asyncio
from FastIO import CopyDir


async def main():
    await CopyDir(r"C:\\", r"D\\backup")

if __name__ == "__main__":
    asyncio.run(main())
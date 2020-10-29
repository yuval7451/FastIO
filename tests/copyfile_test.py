# Author: Yuval Kaneti
# Backup Kernel32.dll

import asyncio
from FastIO import CopyFile
async def main():
   await CopyFile(r"C:\Windows\System32\kernel32.dll", r"D:\backup\kernel32.dll.backup")    

asyncio.run(main())
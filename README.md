# FastIO - *A Faster Asynchronouse IO In Python*
---

### What Is It?

>- *A Fully Asynchronouse shutil like API*
---

### Getting Started

>- *Installation* 
>```
>git clone https://github.com/yuval7451/FastIO.git
>cd FastIO
>pip install -r requirements.txt
>```

---
>- *Usage*
>```
>import asyncio
>from FastIO import CopyDir
>async def main():
>    await CopyDir(r"C:\\", r"D\\backup")
>asyncio.run(main())
>```

---
### API
>- FastIO.walk(...): An AsyncGenerator os.walk like Implementation 
>```
>from FastIO import walk
>async def main():
>    async for basedir, dirs, filenames in walk(r"C:\\"):
>        print(basedir, dirs, filenames)
>asyncio.run(main())
>```

>- FastIO.CopyFile(...): An Asynchronouse shutil.CopyFile Implementation
>```
>from FastIO import CopyFile
>async def main():
>    await CopyFile(r"C:\Windows\System32\kernel32.dll", r"D:\backup\kernel32.dll.backup")    
>asyncio.run(main())
>```

>- FastIO.CopyDir(...): An Asynchronouse shutil.copytree Implementation
>```
>from FastIO import CopyDir
>async def main():
>    await CopyDir(r"C:\\", r"D:\backup\C")    
>asyncio.run(main())
>```

---
### Performance
| Number Of Files | Avg File Size | Total File Sizes | Total Time  |
|-----------------|---------------|------------------|-------------|
| 250             | 3.8MB         | 900 MB           | 10 Seconds  |
| 500             | 1.5MB         | 750MB            | 12 Seconds  |
| 1000            | 7.8MB         | 7.8GB            | 150 Seconds |

# FastIO - *A Faster Asynchronouse IO In Python*
---

### What Is It?

>* *A Fully Asynchronouse & Non-Blcoking shutil like API*
---

### Getting Started

>* *Installation* 
>```
>git clone https://github.com/yuval7451/FastIO.git
>cd FastIO
>pip install -r requirements.txt
>```

---
>* *Usage*
>```
>import asyncio
>from FastIO import CopyDir
>async def main():
>    await CopyDir(r"C:\\", r"D\\backup")
>
>asyncio.run(main())
>```

---
### Performance
#### Disclaimer
> * **These results Were Taken on a Samsung PM951 250GB NVMe ssd, Your Results may very depanding on the R/W Spead of your Drive**
> * **CopyFiles Only Copy The Files were in The destination folder and does not recursively copy Files for sub-directoris**
> * **CopyDir Copy's the enitre Directory structure and mirroes it to the Destination Folder and there for Takes longer**

---
* CopyFiles Performance

| Data Type | Number Of Files | Avg File Size | Total File Sizes | Total Time  |
|-----------|-----------------|---------------|------------------|-------------|
| Images    | 120             | 8.3MB         | 1GB              |  3 Seconds  |
| Images    | 430             | 7MB           | 3GB              | 10 Seconds  |
| Images    | 650             | 7.6MB         | 5GB              | 30 Seconds  |

* CopyDir Performance

| Data Type | Number Of Files | Avg File Size | Total File Sizes | Total Time  |
|-----------|-----------------|---------------|------------------|-------------|
| Images    | 120             | 8.3MB         | 1GB              | 15 Seconds  |
| Images    | 430             | 7MB           | 3GB              | 50 Seconds  |
| Images    | 650             | 7.6MB         | 5GB              | 90 Seconds  |
| Python27  | 15000           | 0.2KB         | 400MB            | 125 Seconds |

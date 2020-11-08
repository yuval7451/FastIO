"""
Author 
------
- Yuval Kaneti.

Purpose
-------
- Asynchronouse Non-Blocking Functions & Coroutines for Preprocessing. 
"""

## Imports
import concurrent.futures
from contextlib import suppress
from functools import partial
from inspect import iscoroutinefunction
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Tuple, Union

import asyncio
from asyncio import Semaphore

from FastIO import Logger
from FastIO.types import FastIOAsyncFetchTypes, FastIOSyncFetchTypes
from FastIO.common import MAX_WORKERS, STRING_OR_BYTES
from FastIO.decorators import async_performance, sync_performance, debug

## Functions
@async_performance
async def AsyncMap(items: Iterable[Any], 
                   process: Callable[[STRING_OR_BYTES], Union[Awaitable[Any], Any]],
                   fetch: Union[FastIOAsyncFetchTypes, Callable[..., Awaitable[STRING_OR_BYTES]]]=FastIOAsyncFetchTypes.FILE,
                   max_workers: int=MAX_WORKERS,
                   **kwargs: Dict[Any, Any]) -> Tuple[Any]:
    """AsyncMap: A High Preformence Asynchronouse Non-Blocking Mapping Function.

    Parameters
    ----------
    items : Iterable[Any]
        an Iterable of Things to be proccesed.
    
    process : Callable[[Union[str, bytes]], Union[Awaitable[Any], Any]]
        A Blocking or Non-Blocking Function that will Proccess the item.
    
    fetch : Union[FastIOAsyncFetchTypes, Callable[..., Awaitable[STRING_OR_BYTES]]], optional
        A Non-Blocking Asynchronous Function the will get the item, by default FastIOAsyncFetchTypes.FILE

    max_workers : int, optional
        The Number of concurrent Coroutines, by default MAX_WORKERS

    NOTE
    ----
    * It's <fetch> job to Get the content of the item in a Non-blocking Asynchronous way.
    * It's <process> job to preprocces the file content and return it when done

    Returns
    -------
    Tuple[Any]
        A Tuple of all the <process> output.
    """    
    semaphore = Semaphore(max_workers)
    loop = asyncio.get_event_loop()
    _AsyncMap = _AsyncMapCoroutine if iscoroutinefunction(process) else _AsyncMapExecutor   
    return await asyncio.gather(*[_AsyncMap(item=item, process=process, fetch=fetch, semaphore=semaphore, loop=loop, **kwargs) for item in items]) # type: ignore

async def _AsyncMapExecutor(item: str, 
                            process: Callable[[STRING_OR_BYTES], Any], 
                            fetch: Union[FastIOAsyncFetchTypes, Callable[..., Awaitable[STRING_OR_BYTES]]],
                            semaphore: asyncio.Semaphore,
                            loop: asyncio.AbstractEventLoop,
                            **kwrags: Dict[Any, Any]) -> Any:
    """_AsyncMapExecutor: A Wraper for blocking preproccesing fucntion.

    Parameters
    ----------
    item : str
        The item.
    
    process : Callable[[Union[str, bytes]], Any]
        A Function to call with the file content.
    
    fetch : Union[FastIOFetchTypes, Callable[..., Awaitable[STRING_OR_BYTES]]], optional
        A Non-Blocking Asynchronous Function the will get the item, by default FastIOFetchTypes.FILE

    semaphore : asyncio.Semaphore
        A Semphore to control the number of concurrent Coroutines.
    
    loop : asyncio.AbstractEventLoop
        The Current Eventloop.

    Returns
    -------
    Any
        The Procesed item Content.
    """    
    async with semaphore:
        item_content = await fetch(item, **kwrags)
        return await loop.run_in_executor(None, partial(process, item_content))

async def _AsyncMapCoroutine(item: str, 
                            process: Callable[[STRING_OR_BYTES], Any], 
                            fetch: Union[FastIOAsyncFetchTypes, Callable[[Any], Awaitable[STRING_OR_BYTES]]],
                            semaphore: asyncio.Semaphore,
                            **kwrags: Dict[Any, Any]) -> Any:
    """_AsyncMapCoroutine: A Wraper for Non-blocking preproccesing fucntion.

    Parameters
    ----------
    item : str
        The File name.
    
    process : Callable[[Union[str, bytes]], Any]
        A Function to call with the file content.
    
    fetch : Union[FastIOFetchTypes, Callable[..., Awaitable[STRING_OR_BYTES]]], optional
        A Non-Blocking Asynchronous Function the will get the item, by default FastIOFetchTypes.FILE

    semaphore : asyncio.Semaphore
        A Semphore to control the number of concurrent Coroutines.
    
    Returns
    -------
    Any
        The Procesed file Content.
    """   
    async with semaphore:
        item_content = await fetch(item, **kwrags) # type: ignore
        return await process(item_content)

@sync_performance
def ThreadedMap(items: Iterable[Any], 
                process: Callable[[STRING_OR_BYTES], Any],
                fetch: Union[FastIOSyncFetchTypes, Callable[..., STRING_OR_BYTES]]=FastIOSyncFetchTypes.FILE,
                max_workers: int=MAX_WORKERS,
                **kwargs: Dict[Any, Any]) -> List[Any]:

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_processed = [executor.submit(_ThreadedMapExecutor, item, process, fetch, **kwargs) for item in items]
        for future in concurrent.futures.as_completed(future_to_processed):
                results.append(future.result())

    return results

def _ThreadedMapExecutor(item: str, 
                        process: Callable[[STRING_OR_BYTES], Any],
                        fetch: Union[FastIOSyncFetchTypes, Callable[..., STRING_OR_BYTES]],
                        **kwargs: Dict[Any, Any]) -> Any:

    item_content = fetch(item, **kwargs) # type: ignore
    return process(item_content, **kwargs)

@async_performance
async def ProduceConsume(producer: Callable, 
                        consumer: Callable,
                        queue: asyncio.Queue,
                        loop: Optional[asyncio.AbstractEventLoop]=None,
                        **kwargs) -> Tuple:
    if loop is None:
        loop = asyncio.get_event_loop()
    _producer = producer(queue, **kwargs)
    _consumer = consumer(queue, **kwargs)
    return await asyncio.gather(_producer, _consumer)


@async_performance
async def Producer(queue: asyncio.Queue,
                   items: Iterable,
                   fetch: Callable,
                   **kwargs: Dict) -> None:

    await asyncio.gather(*[queue.put(await fetch(item, **kwargs))  for item in items])
    await queue.put(None)

@async_performance
async def Consumer(queue: asyncio.Queue,
                   process: Callable,
                   **kwargs: Dict) -> list:
    results = []
    loop = asyncio.get_event_loop()
    while True:
        item = await queue.get()
        if item is None:
            # the producer emits None to indicate that it is done
            break
        results.append(
            await loop.run_in_executor(None, 
                    partial(process, item, **kwargs)
            )
        )

    return results

    
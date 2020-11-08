

## Imports

import time

from functools import wraps
from typing import Any,  Callable, Coroutine

from FastIO import Logger
from FastIO.common import DEBUG

## Decorators
def async_performance(func: Callable[..., Any]) -> Callable[..., Coroutine]:
    """performance: A Decorator for measuring performance. 

    Parameters
    ----------
    func : Callable[..., Any]
        A Callable Function.

    Returns
    -------
    Callable[..., Coroutine]
        The Callble function output.
    """    
    @wraps(func)
    async def _performance(*args, **kwargs):
        if DEBUG:
            start = time.time()
            result = await func(*args, **kwargs)
            end = time.time()
            Logger.debug(f"Function <{func.__name__}> took {end - start} seconds to execute")
            return result
        else:
            return await func(*args, **kwargs)
    return _performance

def sync_performance(func: Callable[..., Any]) -> Callable[..., Any]:
    """performance: A Decorator for measuring performance. 

    Parameters
    ----------
    func : Callable[..., Any]
        A Callable Function.

    Returns
    -------
    Callable[..., Coroutine]
        The Callble function output.
    """    
    @wraps(func)
    def _performance(*args, **kwargs):
        if DEBUG:
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            Logger.debug(f"Function <{func.__name__}> took {end - start} seconds to execute")
            return result
        else:
            return func(*args, **kwargs)
    return _performance

def debug(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def _debug(*args, **kwargs):
        if DEBUG:
            for arg in args:
                Logger.debug(f"arg: {type(arg)} = {arg}")
            for name, kwarg in kwargs.items():
                Logger.debug(f"kwarg: {name}: {type(kwarg)} = {kwarg}")
            result = func(*args, **kwargs)
            return result
        else:
            Logger.warn(f"@debug was called at: {func.__name__} but DEBUG is False")
            return func(*args, **kwargs)
    return _debug
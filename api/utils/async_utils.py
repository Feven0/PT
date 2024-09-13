import os
import functools
import asyncio

from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

def force_async(fn):
    '''
    turns a sync function to async function using threads
    '''
    from concurrent.futures import ThreadPoolExecutor
    import asyncio
    pool = ThreadPoolExecutor()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # make it awaitable

    return wrapper


def force_sync(fn):
    '''
    turn an async function to sync function
    '''
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        res = asyncio.wait(fn(*args, **kwargs))
        if asyncio.iscoroutine(res):
            return asyncio.get_event_loop().run_until_complete(res)
        return res

    return wrapper

def run_async(fn, *args, **kwargs):
    '''
    run async function in sync way
    '''
    
    loop = asyncio.get_event_loop()
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None
        
    if loop and loop.is_running():
        print('Async event loop already running. Adding coroutine to the event loop.')
        try:
            tsk = loop.create_task(fn(*args, **kwargs))
            return loop.run_until_complete(asyncio.gather(tsk))
        except Exception as e:
            logger.error(f'Error running async function: {e}')            
            raise
    else:
        return asyncio.run(fn(*args, **kwargs))
 
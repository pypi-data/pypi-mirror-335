import asyncio

def run_async_function(func, *args, **kwargs):
    """Runs an async function in a way that's safe for both scripts and Jupyter notebooks."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import nest_asyncio
        nest_asyncio.apply()
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"The provided function `{func.__name__}` is not asynchronous.")
        # Get coroutine directly
        coro = func(*args, **kwargs)
        # Run the coroutine in the current loop
        result = loop.run_until_complete(coro)

        return result

    else:
        # If not in an event loop, use asyncio.run()
        return asyncio.run(func(*args, **kwargs))
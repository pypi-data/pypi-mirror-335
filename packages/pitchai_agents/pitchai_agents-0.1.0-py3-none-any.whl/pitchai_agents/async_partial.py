async def async_partial(func, *args, **kwargs):
    """Wrapper to create an async-compatible partial function."""
    async def wrapped(*more_args, **more_kwargs):
        return await func(*args, *more_args, **kwargs, **more_kwargs)
    return wrapped
import asyncio
import inspect
import time


async def retry_async(func, *args, sleep_time=1, max_attempts=5, backoff=1, exceptions=(Exception,), **kwargs):
    """
    Retry an asynchronous function up to `max_attempts` times with exponential backoff.

    Parameters:
        func (callable): The async function to be executed.
        *args: Positional arguments for `func`.
        sleep_time (float): Initial delay (in seconds) before retrying.
        max_attempts (int): Maximum number of attempts.
        backoff (float): Factor by which the delay increases after each attempt.
        exceptions (tuple): A tuple of exception types to catch and retry.
        **kwargs: Keyword arguments for `func`.

    Returns:
        The return value of `func` if it succeeds.

    Raises:
        Exception: The last exception encountered after all attempts have failed.
    """
    delay = sleep_time
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            if attempt == max_attempts:
                raise e
            await asyncio.sleep(delay)
            delay *= backoff


def retry(func, *args, sleep_time=1, max_attempts=5, backoff=1, exceptions=(Exception,), **kwargs):
    """
    Retry a function (synchronous or asynchronous) up to `max_attempts` times with exponential backoff.

    For asynchronous functions, this returns an awaitable that must be awaited.

    Parameters:
        func (callable): The function to be executed (sync or async).
        *args: Positional arguments for `func`.
        sleep_time (float): Initial delay (in seconds) before retrying.
        max_attempts (int): Maximum number of attempts.
        backoff (float): Factor by which the delay increases after each attempt.
        exceptions (tuple): A tuple of exception types to catch and retry.
        **kwargs: Keyword arguments for `func`.

    Returns:
        The return value of `func` if it succeeds. For async functions,
        this is an awaitable that yields the result.

    Raises:
        Exception: The last exception encountered after all attempts have failed.
    """
    if inspect.iscoroutinefunction(func):
        return retry_async(
            func,
            *args,
            sleep_time=sleep_time,
            max_attempts=max_attempts,  # Corrected here from 'ax_attempts'
            backoff=backoff,
            exceptions=exceptions,
            **kwargs
        )

    delay = sleep_time
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            if attempt == max_attempts:
                raise e
            time.sleep(delay)
            delay *= backoff

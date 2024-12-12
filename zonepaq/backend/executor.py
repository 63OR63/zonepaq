from concurrent.futures import ThreadPoolExecutor
from functools import wraps

executor = ThreadPoolExecutor()


def run_in_executor(func):
    """Decorator to run methods asynchronously using ThreadPoolExecutor."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return executor.submit(func, *args, **kwargs)

    return wrapper

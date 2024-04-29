import logging
import time
from pathlib import Path


def timeit(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Function {func.__name__} took {time.time() - start} seconds")
        return result

    return wrapper


def log_execution_time(logger, level=logging.INFO):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                file_name = Path(func.__code__.co_filename).name
                logger.log(level, "-" * 90)
                logger.log(level, f"# Starting execution from {file_name}")
                logger.log(level, "-" * 90)
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                execution_time = end_time - start_time
                logger.log(level, f"Finished execution of {file_name}. Execution time: {execution_time:.2f} seconds")
            except Exception as ex:
                logger.error(f"An error occurred in function {file_name}: {str(ex)}", exc_info=True)
                raise
            else:
                return result

        return wrapper

    return decorator


def log_time(logger, level=logging.INFO):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            logger.log(level, f"Function {func.__name__} took {execution_time:.2f} seconds")
            return result

        return wrapper

    return decorator

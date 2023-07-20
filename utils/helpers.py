import logging
import time
from datetime import datetime
from pathlib import Path

from rest_framework.exceptions import ParseError


def string_to_date(date_str):
    if isinstance(date_str, str):
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.isoformat()
    elif isinstance(date_str, datetime):
        return date_str
    else:
        raise TypeError(f"Expected str or datetime, but got {type(date_str)}")


def parse_date(date_str):
    formats = ["%d-%m-%Y %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ParseError(f"Invalid date format: {date_str}")


def format_date_range(start_date, end_date, datefmt="%d-%m-%Y", timefmt="%H:%M:%S"):
    start_date_str = start_date.strftime(datefmt)
    start_time_str = start_date.strftime(timefmt)
    end_date_str = end_date.strftime(datefmt)
    end_time_str = end_date.strftime(timefmt)

    duration = f"{round((end_date - start_date).total_seconds() / 60, 1)} min"

    return (
        f"{start_date_str} ({start_time_str} - {end_time_str}) - {duration}"
        if start_date.date() == end_date.date()
        else f"{start_date_str} {start_time_str} - {end_date_str} {end_time_str} - {duration}"
    )


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

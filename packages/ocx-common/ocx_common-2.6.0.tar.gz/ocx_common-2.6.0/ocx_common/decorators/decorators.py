#  Copyright (c) 2024.  OCX Consortium https://3docx.org. See the LICENSE
"""Reusable decorators"""

# System imports
import time
from functools import wraps
from typing import Dict

# Third party imports
from loguru import logger
from icecream import ic


def timer(func):
    """@timer decorator for measuring elapsed time of a function call."""

    @wraps(func)
    def inner_func(*args, **kwargs):
        # start the timer
        start_time = time.time()
        # call the decorated function
        result = func(*args, **kwargs)
        # remeasure the time
        end_time = time.time()
        # compute the elapsed time and print it
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        # return the result of the decorated function execution
        return result

    # return reference to the wrapper function
    return inner_func


def exception_handler(exception_to_raise: BaseException):
    """@exception_handler decorator"""

    def outer_func(func):
        @wraps(func)
        def inner_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Handle the exception
                print(f"An exception occurred: {str(e)}")
                logger.exception(f"An exception occurred: {str(e)}")
                # Optionally, perform additional error handling or logging
                # Reraise the exception if needed
                raise exception_to_raise from e

        return inner_func

    return outer_func


def debugger(func):
    """@debug decorator using ice cream"""

    def wrapper(*args, **kwargs):
        # print the function name and arguments
        for arg in args:
            ic(arg)
        # call the function
        result = func(*args, **kwargs)
        # print the results
        ic(result)
        logger.debug(f"{func.__name__} returned: {result}")
        return result

    return wrapper


def memoize(func):
    """@memoize decorator"""
    cache: Dict = {}

    def wrapper(*args, **kwargs):
        if args in cache:
            return cache[args]
        else:
            result = func(*args)
            cache[args] = result
            return result

    return wrapper

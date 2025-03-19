from functools import wraps
from typing import Callable
import logging

from easy_serverless.aws.helpers import is_lambda_invoke, lambda_invoke


def easy_lambda(func: Callable = None, unpack_lists: bool = False, ) -> Callable:
    """
    'easy_lambda' is a decorator that will automatically unpack the key/values from a aws lambda event into the
    arguments of a python function.

    :param unpack_lists: Whether to unpack a json array into the positional arguments of the decorated function.
    :param func: The function to be decorated.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug(f"Args: {args}")
        logging.debug(f"Kwargs: {kwargs}")
        # TODO: Async functions
        if is_lambda_invoke(*args, **kwargs):
            result = lambda_invoke(func, *args, unpack_lists=unpack_lists)
        else:
            result = func(*args, **kwargs)
        return result

    return wrapper


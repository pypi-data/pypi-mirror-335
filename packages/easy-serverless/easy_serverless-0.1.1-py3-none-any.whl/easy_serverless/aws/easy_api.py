from functools import wraps
from typing import Callable, Optional, Iterable
import logging

from easy_serverless.aws.helpers import is_api_invoke, \
    api_gateway_invoke, http_methods


def _easy_api(method: http_methods, success_code: int = 200, body: Optional[Iterable[str]] = None,
              headers: Optional[Iterable[str]] = None, query_params: Optional[Iterable[str]] = None,
              path_params: Optional[Iterable[str]] = None, stage_vars: Optional[Iterable[str]] = None,
              unpack_lists: bool = True):
    def outer_wrapper(func: Callable):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            logging.debug(f"Args: {args}")
            logging.debug(f"Kwargs: {kwargs}")
            if is_api_invoke(*args, **kwargs):
                result = api_gateway_invoke(func, *args, method=method, response_code=success_code,
                                            body=body, headers=headers, query_params=query_params,
                                            path_params=path_params, stage_vars=stage_vars,
                                            unpack_lists=unpack_lists)
            else:
                result = func(*args, **kwargs)
            return result

        return inner_wrapper

    return outer_wrapper

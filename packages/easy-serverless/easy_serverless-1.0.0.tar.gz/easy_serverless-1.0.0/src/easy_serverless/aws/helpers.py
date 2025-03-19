import json
import logging
from inspect import signature
from typing import Optional, Iterable, Literal, Dict, Union, Any, List, Type, Sequence, TypedDict

http_methods = Literal["GET", "PUT", "POST", "DELETE"]

JSON_BASE_TYPES = Union[int, str, float, bool, Type[None]]

JSON = Union[Dict[str, Any], List[Any], JSON_BASE_TYPES]


class HttpResponseType(TypedDict):
    body: JSON
    statusCode: int
    headers: Optional[Dict[str, JSON_BASE_TYPES]]
    cookies: Optional[Sequence[str]]
    isBase64Encoded: bool


class RestResponseType(TypedDict):
    body: JSON
    statusCode: int
    headers: Optional[Dict[str, JSON_BASE_TYPES]]
    multiValueHeaders: Dict[str, Union[Sequence[JSON_BASE_TYPES], JSON_BASE_TYPES]]
    isBase64Encoded: bool


def is_lambda_invoke(*args, **kwargs) -> bool:
    if len(args) == 2 and isinstance(args[1], dict) and args[1].get("function_name") is not None:
        return True
    else:
        return False


def is_api_invoke(*args, **kwargs) -> bool:
    response = False
    if is_lambda_invoke(*args, **kwargs):
        context = args[0].get("requestContext", {})
        if context.get("httpMethod") is not None or context.get("http", {}).get("Method") is not None:
            response = True
    return response


def lambda_invoke(func, event, context, unpack_lists: bool = True, return_errors: bool = False):
    logging.debug("Direct lambda invoke detected.")
    logging.debug(f"Event: {event}")
    logging.debug(f"Context: {context}")

    unbound_sig = signature(func)
    error = None
    if isinstance(event, dict):
        try:
            bound_sig = unbound_sig.bind(**event)
        except TypeError as e:
            error = TypeError(f"Dictionary (json) input was unable to be bound to function signature: {e}")

    elif not any(param.kind in {param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY}
                 for param in unbound_sig.parameters.values()):
        error = TypeError("This function has no positional args please reformat the event as a dictionary.")

    elif isinstance(event, list):
        try:
            if unpack_lists:
                bound_sig = unbound_sig.bind(*event)
            else:
                bound_sig = unbound_sig.bind(event)
        except TypeError as e:
            error = TypeError(f"List input was unable to be bound to function signature: {e}")
    elif isinstance(event, str) or isinstance(event, int) or isinstance(event, float) or event is None:
        try:
            bound_sig = unbound_sig.bind(event)
        except TypeError as e:
            error = TypeError(f"{type(event)} input was unable to be bound to function signature: {e}")
    else:
        error = TypeError(f"EasyLambda doesn't know how to handle lambda invocations with type: {type(event)}")

    if error is None:
        try:
            return func(*bound_sig.args, **bound_sig.kwargs)
        except Exception as e:
            error = e

    if return_errors:
        return {"ErrorType": type(error).__name__,
                "ErrorMessage": str(error)}
    else:
        raise error


def api_gateway_invoke(func, event, context, method: http_methods, response_code: int = 200,
                       body: Optional[Iterable[str]] = None, headers: Optional[Iterable[str]] = None,
                       query_params: Optional[Iterable[str]] = None, path_params: Optional[Iterable[str]] = None,
                       stage_vars: Optional[Iterable[str]] = None, unpack_lists: bool = True):
    ...


def http_response(body: JSON, status_code: int = 200,
                  headers: Dict[str, JSON_BASE_TYPES] = {"content-type": "application/json"},
                  cookies: Sequence[str] = [], base64_encoded: bool = False) -> HttpResponseType:
    return {"cookies": cookies,
            "isBase64Encoded": base64_encoded,
            "statusCode": status_code,
            "headers": headers,
            "body": body}


def rest_response(body: JSON, status_code: int = 200,
                  headers: Dict[str, Union[Sequence[JSON_BASE_TYPES], JSON_BASE_TYPES]] = {"content-type": "application/json"},
                  base64_encoded: bool = False) -> RestResponseType:
    return {"multiValueHeaders": headers,
            "isBase64Encoded": base64_encoded,
            "statusCode": status_code,
            "headers": {},
            "body": body}

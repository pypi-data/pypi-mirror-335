import functools
from typing import Callable, TypeVar, Any

from flask import _app_ctx_stack

TFn = TypeVar("TFn", bound=Callable[..., Any])


DEFAULT_OBJ = object()


def cached_per_request(key: str) -> Callable[[TFn], TFn]:
    def wrapper(fn: Callable[[...], Any]) -> Any:  # type: ignore
        @functools.wraps(fn)
        def wr(*args: Any, **kwargs: Any) -> Any:
            cached_res = getattr(_app_ctx_stack.top, key, DEFAULT_OBJ)
            if cached_res is not DEFAULT_OBJ:
                return cached_res
            res = fn(*args, **kwargs)
            setattr(_app_ctx_stack.top, key, res)
            return res
        return wr
    return wrapper

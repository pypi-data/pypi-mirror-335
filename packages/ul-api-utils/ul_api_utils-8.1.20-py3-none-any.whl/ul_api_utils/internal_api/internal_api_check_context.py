import contextlib
from typing import Generator, Any, TYPE_CHECKING
from uuid import UUID

from flask import _app_ctx_stack

from ul_api_utils.errors import NotCheckedResponseInternalApiError

if TYPE_CHECKING:
    from ul_api_utils.internal_api.internal_api_response import InternalApiResponse


@contextlib.contextmanager
def internal_api_check_context() -> Generator[None, None, None]:
    _app_ctx_stack.top._api_utils_internal_api_context = []  # type: ignore

    try:
        yield

        invalid_resp = []
        for resp in _app_ctx_stack.top._api_utils_internal_api_context:  # type: ignore
            if not resp._internal_use__checked_once:
                invalid_resp.append(resp)

        if len(invalid_resp) > 0:
            info = ", ".join(f"\"{r._internal_use__info}\"" for r in invalid_resp)
            raise NotCheckedResponseInternalApiError(
                f'internal api responses must be checked once at least :: [{info}]',
            )
    finally:
        _app_ctx_stack.top._api_utils_internal_api_context.clear()  # type: ignore


def internal_api_check_context_add_response(resp: 'InternalApiResponse[Any]') -> None:
    if hasattr(_app_ctx_stack, 'top') and hasattr(_app_ctx_stack.top, '_api_utils_internal_api_context'):
        _app_ctx_stack.top._api_utils_internal_api_context.append(resp)  # type: ignore


def internal_api_check_context_rm_response(id: UUID) -> None:
    if hasattr(_app_ctx_stack, 'top') and hasattr(_app_ctx_stack.top, '_api_utils_internal_api_context'):
        prev = _app_ctx_stack.top._api_utils_internal_api_context  # type: ignore
        _app_ctx_stack.top._api_utils_internal_api_context = [r for r in prev if r.id != id]  # type: ignore

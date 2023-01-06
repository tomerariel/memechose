from typing import Callable, Optional, Any
from functools import wraps
from django.http import HttpResponseServerError, JsonResponse, HttpResponse
from api.errors import AppError


def retry(
    to_catch: Optional[tuple[type]] = None,
    to_raise: type = Exception,
    error_message: str = "An unexpected error has occurred",
    retries: int = 3,
) -> Callable[..., Any]:
    if not isinstance(retries, int) or retries < 1:
        raise ValueError("retries must be a positive integer")

    to_catch = to_catch or (Exception,)
    if isinstance(to_catch, type):
        to_catch = (to_catch,)

    def decorator(f) -> Callable[..., Any]:
        @wraps(f)
        def f_retry(*args, **kwargs):
            for retry in range(retries, -1, -1):
                try:
                    return f(*args, **kwargs)
                except to_catch as e:
                    if retry:
                        continue
                    raise to_raise(error_message) from e

        return f_retry

    return decorator


def request_handler(f) -> Callable[..., HttpResponse]:
    @wraps(f)
    def decorator(*args, **kwargs) -> HttpResponse:
        try:
            return f(*args, **kwargs)
        except AppError as e:
            return JsonResponse(
                status=e.status_code,
                data={"App error": str(e)},
            )
        except Exception as e:
            return HttpResponseServerError(
                f"An unexpected error occurred while processing request: {str(e)}",
            )

    return decorator

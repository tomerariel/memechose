import logging
from functools import wraps
from typing import Callable, Optional

from django.http import HttpResponse, HttpResponseServerError, JsonResponse

from api.errors import AppError


def retry(
    to_catch: Optional[tuple[type]] = None,
    to_raise: type = Exception,
    error_message: str = "An unexpected error has occurred",
    retries: int = 3,
):
    """
    Retry the decorated function multiple times.

    Args:
        to_catch (tuple[type], optional): Exceptions which are expected and will be caught.
        Other exceptions will be raised normally. If not provided, all exceptions will be caught.
        to_raise (type, optional): The type of exception to raise after when the function fails to complete.
        Defaults to Exception.
        error_message (str, optional): The error message which will be attached to the raised exception.
        Defaults to "An unexpected error has occurred".
        retries (int, optional): Number of times to re-run the function. Defaults to 3.
    """

    if not isinstance(retries, int) or retries < 1:
        raise ValueError("retries must be a positive integer")

    to_catch = to_catch or (Exception,)
    if isinstance(to_catch, type):  # handle the case where a single exception type is provided
        to_catch = (to_catch,)

    def decorator(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            for retry in range(retries - 1, -1, -1):
                try:
                    return f(*args, **kwargs)
                except to_catch as e:
                    if retry:
                        continue
                    raise to_raise(error_message) from e

        return f_retry

    return decorator


def request_handler(view: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """
    Handle HTTP errors according to error type and status.

    Args:
        view (Callable[..., HttpResponse]): A view function.
    """

    @wraps(view)
    def decorator(*args, **kwargs) -> HttpResponse:
        try:
            return view(*args, **kwargs)
        except AppError as e:
            logging.exception(f"An app error occurred with status code {e.status_code}")
            return JsonResponse(
                status=e.status_code,
                data={"App error": str(e)},
            )
        except Exception as e:
            logging.exception("An unexpected error occurred")
            return HttpResponseServerError(
                f"An unexpected error occurred while processing request: {str(e)}",
            )

    return decorator

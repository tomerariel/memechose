import random
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from api.errors import UrlNotFound, InvalidUrl, ExpiredUrl, AppError
from api.utils import retry
from api.models import Url
from api.consts import ALLOWED_CHARACTERS, SHORT_URL_LENGTH, MAX_RETRIES_FOR_URL_CLASH


def _generate_short_url() -> str:
    return "".join(random.choice(ALLOWED_CHARACTERS) for _ in range(SHORT_URL_LENGTH))


def _get_url_entry_from_short_url(short_url: str) -> Url:
    try:
        return Url.objects.get(pk=short_url)
    except Url.DoesNotExist as e:
        raise UrlNotFound(short_url) from e


def get_redirect_url(short_url: str) -> str:
    url = _get_url_entry_from_short_url(short_url)
    if url.is_expired:
        raise ExpiredUrl(url.short)
    url.increment_hits()
    return url.long


def create_short_url(long_url: str) -> str:
    if not long_url:
        raise AppError("Please provide a URL")
    if not _is_url_valid(long_url):
        raise InvalidUrl(long_url)
    url_entry: Url = _create_url_entry_with_retry(long_url)
    return url_entry.short


@retry(
    to_raise=AppError,
    error_message="Error generating short URL, please try again momentarily",
    retries=MAX_RETRIES_FOR_URL_CLASH,
)
def _create_url_entry_with_retry(long_url: str) -> Url:
    url_entry, is_available = Url.objects.get_or_create(
        short=_generate_short_url(),
        long=long_url,
    )
    if is_available:
        return url_entry
    raise ValueError()


def _is_url_valid(url: str) -> bool:
    try:
        URLValidator()(url)
    except ValidationError:
        return False
    return True

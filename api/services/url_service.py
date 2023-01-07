import random
from contextlib import suppress
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db.models import F, QuerySet
from django.utils import timezone

from api.consts import ALLOWED_CHARACTERS, MAX_RETRIES_FOR_URL_CLASH, SHORT_URL_LENGTH
from api.decorators import retry
from api.errors import AppError, ExpiredUrl, InvalidUrl, ShortUrlTaken, UrlNotFound
from api.models import Url


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


def get_or_create_short_url(long_url: str) -> str:
    if not _is_url_valid(long_url):
        raise InvalidUrl(long_url)
    return _create_url_entry_with_retry(long_url).short


@retry(
    to_catch=ShortUrlTaken,
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
    raise ShortUrlTaken()


def _is_url_valid(url: str) -> bool:
    with suppress(ValidationError):
        URLValidator()(url)
        return True
    return False


def retrieve_expired_urls(grace_days: int) -> QuerySet[Url]:
    cutoff_time = timezone.now() + timedelta(days=grace_days)
    return (
        Url.objects.annotate(expiry_time=F("time_to_live") + F("created_at"))
        .filter(expiry_time__lt=cutoff_time)
        .order_by("created_at")
        .only("short")
    )

from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone
from api.consts import DEFAULT_EXPIRATION_PERIOD_DAYS, SHORT_URL_LENGTH


def get_default_expiry_time() -> datetime:
    return timezone.now() + timedelta(days=DEFAULT_EXPIRATION_PERIOD_DAYS)


class Url(models.Model):
    short = models.CharField(max_length=SHORT_URL_LENGTH, primary_key=True)
    long = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    expiry_time = models.DateTimeField(default=get_default_expiry_time)
    hits = models.BigIntegerField(default=0)

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expiry_time

    def increment_hits(self) -> None:
        self.hits += 1
        self.save()

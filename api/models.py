from datetime import timedelta

from django.db import models
from django.utils import timezone

from api.consts import DEFAULT_EXPIRATION_PERIOD_DAYS, SHORT_URL_LENGTH

DEFAULT_TTL_TIMEDELTA = timedelta(days=DEFAULT_EXPIRATION_PERIOD_DAYS)


class Url(models.Model):
    short = models.CharField(max_length=SHORT_URL_LENGTH, primary_key=True)
    long = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    time_to_live = models.DurationField(default=DEFAULT_TTL_TIMEDELTA, null=True)
    hits = models.BigIntegerField(default=0)

    @property
    def is_expired(self) -> bool:
        if self.time_to_live is None:
            return False
        return self.created_at + self.time_to_live < timezone.now()

    def increment_hits(self) -> None:
        """
        Increment the hit counter for the URL.
        Ideally, this should be done via an in-memory cache to speed up reads.
        """
        self.hits += 1
        self.save()

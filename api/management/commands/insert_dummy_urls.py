import logging
import random
from datetime import timedelta

from django.core.management.base import BaseCommand

from api.models import Url
from api.services import url_service

log = logging.getLogger(__name__)


def random_ttl() -> timedelta:
    return timedelta(days=random.randint(0, 30))


class Command(BaseCommand):
    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "-a",
            "--amount",
            dest="amount",
            type=int,
        )

    def handle(self, *args, **options) -> None:
        Url.objects.bulk_create(
            Url(
                short=url_service._generate_short_url(),
                long="https://stackoverflow.com/",
                time_to_live=random_ttl(),
            )
            for _ in range(options["amount"])
        )

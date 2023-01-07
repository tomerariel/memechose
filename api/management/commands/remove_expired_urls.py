import logging
import os
from datetime import datetime

from django.core.management.base import BaseCommand

from api.consts import (
    DEFAULT_EXPIRED_URLS_ITERATION_BATCH_SIZE,
    DEFAULT_GRACE_PERIOD_DAYS,
)
from api.models import Url
from api.services import url_service
from api.utils import iterate_in_batches

log = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self) -> None:
        self.expired_urls = None
        self.total_expired_urls = None
        self.batch_size = None
        self.filename = f"remove_expired_urls_job_{str(datetime.now().date())}"

    help = "Remove expired entries from the DB"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "-g",
            "--grace-period",
            dest="grace_period",
            type=int,
            help="grace period for expired entries (days)",
            default=DEFAULT_GRACE_PERIOD_DAYS,
        )

        parser.add_argument(
            "-b",
            "--batch-size",
            dest="batch_size",
            type=int,
            help="iteration batch size",
            default=DEFAULT_EXPIRED_URLS_ITERATION_BATCH_SIZE,
        )

    def handle(self, *args, **options) -> None:
        """
        This command is designed to be run periodically, ideally during low-traffic hours.
        It will remove expired entries from the DB to keep the data fresh and maintain efficient reads.
        The removed data should ideally be written to some persistent storage for analytical needs.

        Due to the potentially massive amount of records, we can't just load the entire queryset to memory.
        Therefore, we first iterate the queryset in batches, write the PKs to a file and then delete
        (again in batches) all records using the file as a guide.
        This process ensures that we can delete all records.
        """
        self.expired_urls = url_service.retrieve_expired_urls(
            grace_days=options["grace_period"]
        )
        self.total_expired_urls = self.expired_urls.count()
        self.batch_size = options["batch_size"]
        self.write_expired_urls_to_file()
        self.remove_expired_urls()
        self.delete_file()
        logging.info(f"Removed {self.total_expired_urls} expired urls")

    def write_expired_urls_to_file(self) -> None:
        with open(self.filename, "w") as file:
            for batch in iterate_in_batches(
                items=self.expired_urls,
                total=self.total_expired_urls,
                batch_size=self.batch_size,
            ):
                short_urls = "\n".join(url.short for url in batch)
                file.writelines(short_urls + "\n")

    def remove_expired_urls(self) -> int:
        with open(self.filename, "r") as file:
            for batch in iterate_in_batches(
                items=file.readlines(),
                total=self.total_expired_urls,
                batch_size=self.batch_size,
            ):
                short_urls = tuple(map(str.strip, batch))
                # in real-world scenarios we would not delete this data, but rather
                # redirect it for future usage.
                Url.objects.filter(short__in=short_urls).delete()

    def delete_file(self) -> None:
        os.remove(self.filename)

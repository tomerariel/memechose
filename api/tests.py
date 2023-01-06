from django.test import TestCase
from api.models import Url
from api.services import url_service
from api.errors import InvalidUrl, ExpiredUrl
from datetime import timedelta
from api.consts import DEFAULT_EXPIRATION_PERIOD_DAYS


class UrlTestCase(TestCase):
    VALID_URL = "https://stackoverflow.com/"

    def _get_valid_entry(self) -> Url:
        short_url = url_service.create_short_url(self.VALID_URL)
        return url_service._get_url_entry_from_short_url(short_url)

    def test_short_url_length(self) -> None:
        short_url = url_service.create_short_url(self.VALID_URL)
        assert len(short_url) == url_service.SHORT_URL_LENGTH

    def test_short_url_redirects_to_correct_long_url(self) -> None:
        short_url = url_service.create_short_url(self.VALID_URL)
        long_url = url_service.get_redirect_url(short_url)
        assert long_url == self.VALID_URL

    def test_new_entry_has_no_hits(self) -> None:
        url_entry = self._get_valid_entry()
        assert not url_entry.hits

    def test_create_invalid_url_fails(self) -> None:
        with self.assertRaises(InvalidUrl):
            invalid_url = self.VALID_URL.replace("/", "@")
            url_service.create_short_url(invalid_url)

    def test_new_entry_has_correct_expiry_date(self) -> None:
        entry = self._get_valid_entry()
        assert (entry.expiry_time - entry.created_at).seconds == 0

    def test_expired_url_fails(self) -> None:
        entry = self._get_valid_entry()
        entry.expiry_time -= timedelta(
            days=DEFAULT_EXPIRATION_PERIOD_DAYS, seconds=1
        )
        entry.save()
        assert entry.is_expired
        with self.assertRaises(ExpiredUrl):
            url_service.get_redirect_url(entry.short)

    def test_hits_are_incremented(self) -> None:
        entry = self._get_valid_entry()
        hits = entry.hits
        url_service.get_redirect_url(entry.short)
        assert url_service._get_url_entry_from_short_url(entry.short).hits == hits + 1

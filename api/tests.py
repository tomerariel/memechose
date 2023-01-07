from django.test import TestCase

from api.errors import ExpiredUrl, InvalidUrl
from api.models import Url, DEFAULT_TTL_TIMEDELTA
from api.services import url_service


class UrlTestCase(TestCase):
    VALID_URL = "https://stackoverflow.com/"

    def _create_valid_entry(self) -> Url:
        short_url = url_service.get_or_create_short_url(self.VALID_URL)
        return url_service._get_url_entry_from_short_url(short_url)

    def test_short_url_length(self) -> None:
        short_url = url_service.get_or_create_short_url(self.VALID_URL)
        self.assertEqual(len(short_url), url_service.SHORT_URL_LENGTH)

    def test_short_url_redirects_to_correct_long_url(self) -> None:
        short_url = url_service.get_or_create_short_url(self.VALID_URL)
        long_url = url_service.get_redirect_url(short_url)
        self.assertEqual(long_url, self.VALID_URL)

    def test_new_entry_has_no_hits(self) -> None:
        url_entry = self._create_valid_entry()
        self.assertEqual(url_entry.hits, 0)

    def test_create_invalid_url_fails(self) -> None:
        with self.assertRaises(InvalidUrl):
            invalid_url = self.VALID_URL.replace("/", "@")
            url_service.get_or_create_short_url(invalid_url)

    def test_new_entry_has_correct_expiry_date(self) -> None:
        entry = self._create_valid_entry()
        self.assertEqual(entry.time_to_live, DEFAULT_TTL_TIMEDELTA)

    def test_expired_url_fails(self) -> None:
        entry = self._create_valid_entry()
        entry.time_to_live -= DEFAULT_TTL_TIMEDELTA
        entry.save()
        self.assertTrue(entry.is_expired)
        with self.assertRaises(ExpiredUrl):
            url_service.get_redirect_url(entry.short)

    def test_hits_are_incremented_on_redirect(self) -> None:
        entry = self._create_valid_entry()
        current_hits = entry.hits
        url_service.get_redirect_url(entry.short)
        post_redirect_hits = url_service._get_url_entry_from_short_url(entry.short).hits
        self.assertEqual(post_redirect_hits, current_hits + 1)

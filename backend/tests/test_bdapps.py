"""
GhoraGhuri — bdapps Client Tests
Tests MSISDN formatting and client utilities.
"""
from app.services.bdapps.client import BdAppsClient


class TestMsisdnFormatting:
    """Test phone number format conversions."""

    def test_local_to_tel(self):
        assert BdAppsClient.format_msisdn("01812345678") == "tel:8801812345678"

    def test_full_to_tel(self):
        assert BdAppsClient.format_msisdn("8801812345678") == "tel:8801812345678"

    def test_already_tel(self):
        assert BdAppsClient.format_msisdn("tel:8801812345678") == "tel:8801812345678"

    def test_plus_prefix(self):
        assert BdAppsClient.format_msisdn("+8801812345678") == "tel:8801812345678"

    def test_extract_local(self):
        assert BdAppsClient.extract_msisdn("tel:8801812345678") == "01812345678"

    def test_extract_without_prefix(self):
        assert BdAppsClient.extract_msisdn("8801812345678") == "01812345678"

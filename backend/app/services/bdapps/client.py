"""
GhoraGhuri — bdapps Base HTTP Client
Handles common request formatting, authentication, and error handling
for all bdapps TAP API calls.

Base URL: https://developer.bdapps.com
Content-Type: application/json;charset=utf-8
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class BdAppsError(Exception):
    """Raised when a bdapps API call fails."""

    def __init__(self, status_code: str, status_detail: str, raw_response: dict | None = None):
        self.status_code = status_code
        self.status_detail = status_detail
        self.raw_response = raw_response
        super().__init__(f"bdapps error {status_code}: {status_detail}")


class BdAppsClient:
    """
    Low-level HTTP client for bdapps TAP API.

    All bdapps endpoints use POST with JSON body.
    Authentication is via applicationId + password (MD5-hashed key).
    """

    SUCCESS_CODE = "S1000"

    # Common error codes across all bdapps APIs
    ERROR_CODES = {
        "E1303": "IP not provisioned",
        "E1308": "Charging error (e.g., insufficient balance)",
        "E1312": "Invalid request format",
        "E1313": "Authentication failed",
        "E1317": "Invalid MSISDN",
        "E1318": "Rate limit exceeded (per second)",
        "E1319": "Daily transaction limit exceeded",
        "E1325": "Invalid address format",
        "E1326": "Insufficient balance",
        "E1337": "Duplicate request",
        "E1601": "Unexpected system error",
        "E1602": "Delivery failed, retry",
        "E1603": "Temporary system error",
    }

    def __init__(
        self,
        base_url: str | None = None,
        app_id: str | None = None,
        password: str | None = None,
    ):
        self.base_url = (base_url or settings.bdapps_base_url).rstrip("/")
        self.app_id = app_id or settings.bdapps_app_id
        self.password = password or settings.bdapps_password
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialize the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(30.0, connect=10.0),
                headers={
                    "Content-Type": "application/json;charset=utf-8",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _get_timestamp(self) -> str:
        """Generate bdapps-format timestamp: yyMMddHHmmss"""
        return datetime.now().strftime("%y%m%d%H%M%S")

    def _base_payload(self) -> dict[str, str]:
        """Common fields for all bdapps requests."""
        return {
            "applicationId": self.app_id,
            "password": self.password,
        }

    async def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Make a POST request to a bdapps endpoint.

        Args:
            endpoint: API path (e.g., '/otp/request')
            payload: Request body (applicationId + password auto-merged)

        Returns:
            Response JSON dict

        Raises:
            BdAppsError: If statusCode != S1000
            httpx.HTTPError: On network/transport errors
        """
        full_payload = {**self._base_payload(), **payload}

        logger.info(f"bdapps POST {endpoint} | app_id={self.app_id}")
        logger.debug(f"bdapps request payload: {full_payload}")

        client = await self._get_client()

        try:
            response = await client.post(endpoint, json=full_payload)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"bdapps HTTP error: {e.response.status_code} for {endpoint}")
            raise BdAppsError(
                status_code=f"HTTP_{e.response.status_code}",
                status_detail=f"HTTP error: {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            logger.error(f"bdapps request error for {endpoint}: {e}")
            raise BdAppsError(
                status_code="NETWORK_ERROR",
                status_detail=str(e),
            ) from e

        logger.info(
            f"bdapps response {endpoint} | statusCode={data.get('statusCode', 'N/A')}"
        )
        logger.debug(f"bdapps response body: {data}")

        # Check for API-level errors
        status_code = data.get("statusCode", "")
        if status_code and status_code != self.SUCCESS_CODE:
            raise BdAppsError(
                status_code=status_code,
                status_detail=data.get("statusDetail", "Unknown error"),
                raw_response=data,
            )

        return data

    @staticmethod
    def format_msisdn(msisdn: str) -> str:
        """
        Format a phone number to bdapps tel: format.

        Input examples:
            '01812345678' → 'tel:8801812345678'
            '8801812345678' → 'tel:8801812345678'
            'tel:8801812345678' → 'tel:8801812345678'

        Args:
            msisdn: Phone number in any common format

        Returns:
            Formatted 'tel:880XXXXXXXXXX' string
        """
        msisdn = msisdn.strip()

        if msisdn.startswith("tel:"):
            return msisdn

        # Remove any + prefix
        msisdn = msisdn.lstrip("+")

        # Add country code if starting with 0
        if msisdn.startswith("0"):
            msisdn = "880" + msisdn[1:]

        # Add country code if not present
        if not msisdn.startswith("880"):
            msisdn = "880" + msisdn

        return f"tel:{msisdn}"

    @staticmethod
    def extract_msisdn(tel_format: str) -> str:
        """
        Extract local phone number from bdapps tel: format.

        'tel:8801812345678' → '01812345678'
        """
        number = tel_format.replace("tel:", "").strip()
        if number.startswith("880"):
            return "0" + number[3:]
        return number

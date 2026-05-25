"""
GhoraGhuri — bdapps OTP Service
Handles /otp/request and /otp/verify API calls.

Flow:
1. Request OTP → bdapps sends SMS with OTP to subscriber
2. User enters OTP in app
3. Verify OTP → bdapps confirms and returns masked subscriberId
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.services.bdapps.client import BdAppsClient

logger = logging.getLogger(__name__)


@dataclass
class OtpRequestResult:
    """Result of an OTP request."""
    reference_no: str
    status_code: str
    status_detail: str


@dataclass
class OtpVerifyResult:
    """Result of an OTP verification."""
    subscriber_id: str  # masked MSISDN from bdapps
    subscription_status: str  # REGISTERED | UNREGISTERED
    status_code: str
    status_detail: str


class OtpService:
    """
    bdapps OTP authentication service.

    Endpoints:
        POST /otp/request — Send OTP to subscriber MSISDN
        POST /otp/verify  — Verify OTP entered by subscriber
    """

    def __init__(self, client: BdAppsClient | None = None):
        self.client = client or BdAppsClient()

    async def request_otp(
        self,
        msisdn: str,
        application_hash: str | None = None,
        app_metadata: dict[str, str] | None = None,
    ) -> OtpRequestResult:
        """
        Request an OTP for the given phone number.

        bdapps will send an SMS with the OTP to the subscriber.

        Args:
            msisdn: Phone number (e.g., '01812345678')
            application_hash: Optional hash for SMS Retriever API (Android)
            app_metadata: Optional device info {client, device, os, appCode}

        Returns:
            OtpRequestResult with reference_no for verification

        Raises:
            BdAppsError: On API failure (E1853 = max OTP requests reached, etc.)
        """
        formatted = BdAppsClient.format_msisdn(msisdn)

        payload: dict[str, Any] = {
            "subscriberId": formatted,
        }

        if application_hash:
            payload["applicationHash"] = application_hash

        if app_metadata:
            payload["applicationMetaData"] = app_metadata

        logger.info(f"Requesting OTP for {formatted}")
        response = await self.client._post("/otp/request", payload)

        return OtpRequestResult(
            reference_no=response["referenceNo"],
            status_code=response.get("statusCode", "S1000"),
            status_detail=response.get("statusDetail", "Success"),
        )

    async def verify_otp(
        self,
        reference_no: str,
        otp: str,
    ) -> OtpVerifyResult:
        """
        Verify an OTP entered by the subscriber.

        On success, bdapps returns the masked subscriberId which should be
        stored and used for all subsequent API calls (CAAS, etc.).

        Args:
            reference_no: Reference number from request_otp response
            otp: The OTP code entered by the user

        Returns:
            OtpVerifyResult with masked subscriber_id

        Raises:
            BdAppsError:
                E1850 = Invalid OTP
                E1851 = OTP expired
                E1852 = Max attempts reached
                E1854 = OTP not found
                E1855 = Invalid reference number
        """
        payload = {
            "referenceNo": reference_no,
            "otp": str(otp),
        }

        logger.info(f"Verifying OTP for ref={reference_no}")
        response = await self.client._post("/otp/verify", payload)

        return OtpVerifyResult(
            subscriber_id=response.get("subscriberId", ""),
            subscription_status=response.get("subscriptionStatus", "REGISTERED"),
            status_code=response.get("statusCode", "S1000"),
            status_detail=response.get("statusDetail", "Success"),
        )

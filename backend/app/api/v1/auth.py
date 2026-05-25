"""
GhoraGhuri — Auth API Endpoints
OTP login/verify via bdapps integration.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import create_jwt_token, get_language
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    OtpRequestIn, OtpRequestOut,
    OtpVerifyIn, OtpVerifyOut, UserInfo,
)
from app.services.bdapps.client import BdAppsClient, BdAppsError
from app.services.bdapps.otp import OtpService
from app.utils.i18n import t

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

otp_service = OtpService()


@router.post("/otp/request", response_model=OtpRequestOut)
async def request_otp(
    body: OtpRequestIn,
    lang: str = Depends(get_language),
):
    """
    Request an OTP for phone number verification.
    bdapps will send an SMS with the OTP to the subscriber.
    """
    try:
        result = await otp_service.request_otp(
            msisdn=body.msisdn,
            app_metadata=body.device_info,
        )

        return OtpRequestOut(
            reference_no=result.reference_no,
            message=t("otp_sent", "en"),
            message_bn=t("otp_sent", "bn"),
        )

    except BdAppsError as e:
        logger.error(f"OTP request failed: {e}")

        if e.status_code == "E1853":
            raise HTTPException(status_code=429, detail=t("otp_max_attempts", lang))
        elif e.status_code == "E1317":
            raise HTTPException(status_code=400, detail="Invalid phone number")
        else:
            raise HTTPException(status_code=502, detail=f"OTP service error: {e.status_detail}")


@router.post("/otp/verify", response_model=OtpVerifyOut)
async def verify_otp(
    body: OtpVerifyIn,
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """
    Verify OTP and authenticate user.
    Creates user account on first login.
    Returns JWT token for subsequent API calls.
    """
    try:
        result = await otp_service.verify_otp(
            reference_no=body.reference_no,
            otp=body.otp,
        )
    except BdAppsError as e:
        logger.error(f"OTP verify failed: {e}")

        error_map = {
            "E1850": ("otp_invalid", 400),
            "E1851": ("otp_expired", 400),
            "E1852": ("otp_max_attempts", 429),
            "E1854": ("otp_invalid", 400),
            "E1855": ("otp_invalid", 400),
        }

        key, status_code = error_map.get(e.status_code, ("error_unknown", 502))
        raise HTTPException(status_code=status_code, detail=t(key, lang))

    # Extract MSISDN from masked subscriber ID
    masked_subscriber = result.subscriber_id
    local_msisdn = BdAppsClient.extract_msisdn(masked_subscriber) if masked_subscriber else ""

    # Find or create user
    stmt = select(User).where(User.bdapps_subscriber_id == masked_subscriber)
    db_result = await db.execute(stmt)
    user = db_result.scalar_one_or_none()

    if not user and local_msisdn:
        # Also check by MSISDN
        stmt2 = select(User).where(User.msisdn == local_msisdn)
        db_result2 = await db.execute(stmt2)
        user = db_result2.scalar_one_or_none()

    if user:
        # Update subscriber ID if not set
        if not user.bdapps_subscriber_id:
            user.bdapps_subscriber_id = masked_subscriber
    else:
        # Create new user
        user = User(
            msisdn=local_msisdn or "unknown",
            msisdn_full=BdAppsClient.format_msisdn(local_msisdn) if local_msisdn else "",
            bdapps_subscriber_id=masked_subscriber,
            language_pref=lang,
        )
        db.add(user)
        await db.flush()

    # Generate JWT
    token = create_jwt_token(user.id, user.msisdn)

    return OtpVerifyOut(
        token=token,
        user=UserInfo(
            id=user.id,
            msisdn=user.msisdn,
            display_name=user.display_name,
            language_pref=user.language_pref,
            total_contributions=user.total_contributions,
            reputation_score=user.reputation_score,
        ),
    )

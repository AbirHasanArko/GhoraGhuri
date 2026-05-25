"""
GhoraGhuri — Auth Schemas
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class OtpRequestIn(BaseModel):
    """Request OTP for phone number."""
    msisdn: str = Field(
        ...,
        min_length=10,
        max_length=15,
        description="Phone number (e.g., '01812345678')",
        examples=["01812345678"],
    )
    device_info: dict | None = Field(
        None,
        description="Optional device metadata {client, device, os, appCode}",
    )


class OtpRequestOut(BaseModel):
    """OTP request response."""
    reference_no: str
    message: str
    message_bn: str


class OtpVerifyIn(BaseModel):
    """Verify OTP code."""
    reference_no: str = Field(..., description="Reference number from OTP request")
    otp: str = Field(
        ...,
        min_length=4,
        max_length=8,
        description="OTP code received via SMS",
        examples=["123456"],
    )


class OtpVerifyOut(BaseModel):
    """OTP verification response with JWT token."""
    token: str
    refresh_token: str | None = None
    user: UserInfo


class UserInfo(BaseModel):
    """Basic user information."""
    id: str
    msisdn: str
    display_name: str | None = None
    language_pref: str = "bn"
    total_contributions: int = 0
    reputation_score: float = 0.0


# Fix forward reference
OtpVerifyOut.model_rebuild()

"""
GhoraGhuri — Contribution Schemas
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class CrowdReportIn(BaseModel):
    """Report crowd level on a transport edge."""
    edge_id: str | None = None
    node_code: str | None = Field(None, examples=["MIR10"])
    crowd_level: str = Field(..., pattern="^(low|medium|high|extreme)$")
    lat: float | None = None
    lng: float | None = None
    notes: str | None = Field(None, max_length=500)


class RouteVerifyIn(BaseModel):
    """Verify/update transport route data."""
    edge_id: str
    is_active: bool = True
    fare_bdt: float | None = None
    time_minutes: float | None = None
    crowd_level: str | None = Field(None, pattern="^(low|medium|high|extreme)$")
    notes: str | None = Field(None, max_length=500)


class GpsTrackStartIn(BaseModel):
    """Start GPS tracking session."""
    transport_mode: str | None = Field(None, description="Mode being tracked")


class GpsPointIn(BaseModel):
    """Single GPS point."""
    lat: float
    lng: float
    accuracy: float | None = None
    speed: float | None = None
    timestamp: str | None = None


class GpsTrackCompleteIn(BaseModel):
    """Complete GPS tracking session."""
    contribution_id: str
    points: list[GpsPointIn] | None = None  # final batch of points


class ContributionOut(BaseModel):
    """Contribution result."""
    contribution_id: str
    type: str
    reward_coins: int
    message: str
    message_bn: str

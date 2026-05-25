"""
GhoraGhuri — Route Schemas
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class LocationInput(BaseModel):
    """Geographic coordinates."""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)


class RouteRequestIn(BaseModel):
    """Find route request."""
    origin: LocationInput | None = None
    origin_text: str | None = Field(None, max_length=200, examples=["মিরপুর ১০"])
    destination: LocationInput | None = None
    destination_text: str | None = Field(None, max_length=200, examples=["ধানমন্ডি ২৭"])
    optimize: str = Field("time", pattern="^(time|cost|comfort)$")


class RouteStepOut(BaseModel):
    """Single step in route result."""
    step_order: int
    from_name_en: str
    from_name_bn: str
    to_name_en: str
    to_name_bn: str
    transport_mode: str
    instruction_en: str
    instruction_bn: str
    duration_minutes: float
    fare_bdt: float
    distance_meters: float


class RouteResultOut(BaseModel):
    """Complete route result."""
    route_id: str
    steps: list[RouteStepOut]
    total_time_min: float
    total_time_max: float
    total_fare_min: float
    total_fare_max: float
    total_distance_meters: float
    num_transfers: int
    confidence_score: float
    charge_bdt: float
    transaction_id: str | None = None


class RouteErrorOut(BaseModel):
    """Route finding error."""
    success: bool = False
    error: str
    error_bn: str | None = None

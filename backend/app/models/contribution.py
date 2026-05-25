"""
GhoraGhuri — Contribution, GPS Track & SMS Models
"""
from __future__ import annotations

import enum
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import (
    Boolean, DateTime, Enum, Float, Integer, String, Text,
    ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class ContributionType(str, enum.Enum):
    GPS_TRACK = "gps_track"
    CROWD_REPORT = "crowd_report"
    ROUTE_VERIFY = "route_verify"
    STOP_REPORT = "stop_report"


class ValidationStatus(str, enum.Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


class Contribution(Base):
    __tablename__ = "contributions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(
        Enum(ContributionType, name="contribution_type", create_type=False), nullable=False
    )
    location: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    related_edge_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_edges.id")
    )
    related_node_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_nodes.id")
    )
    data_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    validation_status: Mapped[str] = mapped_column(
        Enum(ValidationStatus, name="validation_status", create_type=False),
        default=ValidationStatus.PENDING,
        nullable=False,
    )
    validated_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id")
    )
    reward_coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_rewarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    gps_track: Mapped[GpsTrack | None] = relationship(
        back_populates="contribution", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_contributions_user", "user_id", "created_at"),
        Index("idx_contributions_type", "type", "validation_status"),
    )

    def __repr__(self) -> str:
        return f"<Contribution {self.type} by user={self.user_id}>"


class GpsTrack(Base):
    __tablename__ = "gps_tracks"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    contribution_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("contributions.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    points: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    distance_meters: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    avg_speed_kmh: Mapped[float | None] = mapped_column(Float)
    bounding_box: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POLYGON", srid=4326)
    )
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    contribution: Mapped[Contribution] = relationship(back_populates="gps_track")

    __table_args__ = (
        Index("idx_gps_tracks_contribution", "contribution_id"),
        Index("idx_gps_tracks_user", "user_id"),
    )


class SmsMessage(Base):
    __tablename__ = "sms_messages"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    msisdn: Mapped[str] = mapped_column(String(20), nullable=False)
    direction: Mapped[str] = mapped_column(String(10), nullable=False)  # inbound | outbound
    message: Mapped[str] = mapped_column(Text, nullable=False)
    bdapps_request_id: Mapped[str | None] = mapped_column(String(255))
    related_query_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("route_queries.id")
    )
    status: Mapped[str] = mapped_column(String(20), default="sent")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_sms_msisdn", "msisdn", "created_at"),
    )

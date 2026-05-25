"""
GhoraGhuri — Route Query & Route Step Models
"""
from __future__ import annotations

import enum
from datetime import datetime

from geoalchemy2 import Geography
from sqlalchemy import (
    DateTime, Enum, Float, SmallInteger, String, Text,
    ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CHARGED = "charged"
    FAILED = "failed"
    REFUNDED = "refunded"


class RouteQuery(Base):
    __tablename__ = "route_queries"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    origin_location: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    destination_location: Mapped[str | None] = mapped_column(
        Geography(geometry_type="POINT", srid=4326)
    )
    origin_text: Mapped[str | None] = mapped_column(String(500))
    destination_text: Mapped[str | None] = mapped_column(String(500))
    origin_node_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_nodes.id")
    )
    destination_node_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_nodes.id")
    )
    preferences: Mapped[dict] = mapped_column(JSONB, default={"optimize": "time"})
    result_json: Mapped[dict | None] = mapped_column(JSONB)
    total_time_min: Mapped[float | None] = mapped_column(Float)
    total_time_max: Mapped[float | None] = mapped_column(Float)
    total_fare_min: Mapped[float | None] = mapped_column(Float)
    total_fare_max: Mapped[float | None] = mapped_column(Float)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    charge_bdt: Mapped[float] = mapped_column(Float, default=2.0, nullable=False)
    payment_status: Mapped[str] = mapped_column(
        Enum(PaymentStatus, name="payment_status", create_type=False),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    bdapps_trx_id: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(20), default="app")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    steps: Mapped[list[RouteStep]] = relationship(
        back_populates="query", cascade="all, delete-orphan", order_by="RouteStep.step_order"
    )

    __table_args__ = (
        Index("idx_queries_user", "user_id", "created_at"),
        Index("idx_queries_payment", "payment_status"),
    )


class RouteStep(Base):
    __tablename__ = "route_steps"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    query_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("route_queries.id", ondelete="CASCADE"), nullable=False
    )
    step_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    from_node_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_nodes.id"), nullable=False
    )
    to_node_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_nodes.id"), nullable=False
    )
    edge_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_edges.id")
    )
    transport_mode: Mapped[str] = mapped_column(String(20), nullable=False)
    instruction_en: Mapped[str] = mapped_column(Text, nullable=False)
    instruction_bn: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    fare_bdt: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    distance_meters: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Relationships
    query: Mapped[RouteQuery] = relationship(back_populates="steps")

    __table_args__ = (
        Index("idx_steps_query", "query_id", "step_order"),
    )

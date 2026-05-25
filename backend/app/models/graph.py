"""
GhoraGhuri — Transport Graph Models (Nodes & Edges)
"""
from __future__ import annotations

import enum
from datetime import datetime, time

from geoalchemy2 import Geography
from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, Enum, Float, Integer,
    SmallInteger, String, Time, ForeignKey, Index, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class NodeType(str, enum.Enum):
    BUS_STOP = "bus_stop"
    HUB = "hub"
    RICKSHAW_STAND = "rickshaw_stand"
    LAUNCH_GHAT = "launch_ghat"
    CNG_STAND = "cng_stand"
    INTERSECTION = "intersection"
    TEMPO_STAND = "tempo_stand"
    TRAIN_STATION = "train_station"


class TransportMode(str, enum.Enum):
    BUS = "bus"
    RICKSHAW = "rickshaw"
    CNG = "cng"
    LEGUNA = "leguna"
    TEMPO = "tempo"
    WALKING = "walking"
    LAUNCH = "launch"
    TRAIN = "train"


class CrowdLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class TransportNode(Base):
    __tablename__ = "transport_nodes"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_bn: Mapped[str] = mapped_column(String(200), nullable=False)
    node_type: Mapped[str] = mapped_column(
        Enum(NodeType, name="node_type", create_type=False), nullable=False
    )
    location: Mapped[str] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=False
    )
    address_en: Mapped[str | None] = mapped_column(String(500))
    address_bn: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    outgoing_edges: Mapped[list[TransportEdge]] = relationship(
        back_populates="from_node", foreign_keys="TransportEdge.from_node_id"
    )
    incoming_edges: Mapped[list[TransportEdge]] = relationship(
        back_populates="to_node", foreign_keys="TransportEdge.to_node_id"
    )

    def __repr__(self) -> str:
        return f"<Node {self.code}: {self.name_en}>"


class TransportEdge(Base):
    __tablename__ = "transport_edges"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    from_node_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_nodes.id", ondelete="CASCADE"), nullable=False
    )
    to_node_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_nodes.id", ondelete="CASCADE"), nullable=False
    )
    transport_mode: Mapped[str] = mapped_column(
        Enum(TransportMode, name="transport_mode", create_type=False), nullable=False
    )
    route_name_en: Mapped[str | None] = mapped_column(String(200))
    route_name_bn: Mapped[str | None] = mapped_column(String(200))
    base_time_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    base_fare_bdt: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    distance_meters: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    crowd_level: Mapped[str] = mapped_column(
        Enum(CrowdLevel, name="crowd_level", create_type=False),
        default=CrowdLevel.MEDIUM,
        nullable=False,
    )
    reliability_score: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    is_bidirectional: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    verification_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    from_node: Mapped[TransportNode] = relationship(
        back_populates="outgoing_edges", foreign_keys=[from_node_id]
    )
    to_node: Mapped[TransportNode] = relationship(
        back_populates="incoming_edges", foreign_keys=[to_node_id]
    )
    schedules: Mapped[list[EdgeSchedule]] = relationship(
        back_populates="edge", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("base_time_minutes > 0", name="chk_time_positive"),
        CheckConstraint("base_fare_bdt >= 0", name="chk_fare_non_negative"),
        CheckConstraint(
            "reliability_score >= 0 AND reliability_score <= 1",
            name="chk_reliability_range",
        ),
        CheckConstraint("from_node_id != to_node_id", name="chk_no_self_loop"),
        Index("idx_edges_from_node", "from_node_id", postgresql_where="is_active = true"),
        Index("idx_edges_to_node", "to_node_id", postgresql_where="is_active = true"),
        Index("idx_edges_mode", "transport_mode"),
    )

    def __repr__(self) -> str:
        return f"<Edge {self.from_node_id} → {self.to_node_id} [{self.transport_mode}]>"


class EdgeSchedule(Base):
    __tablename__ = "edge_schedules"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    edge_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("transport_edges.id", ondelete="CASCADE"), nullable=False
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    frequency_minutes: Mapped[float | None] = mapped_column(Float)
    fare_multiplier: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    edge: Mapped[TransportEdge] = relationship(back_populates="schedules")

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 0 AND 6", name="chk_day_range"),
        CheckConstraint("start_time < end_time", name="chk_time_order"),
        Index("idx_schedules_edge", "edge_id"),
    )

"""
GhoraGhuri — User & Session Models
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, Integer, String, Text,
    ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class UserLanguage(str, enum.Enum):
    EN = "en"
    BN = "bn"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    msisdn: Mapped[str] = mapped_column(String(15), unique=True, nullable=False, index=True)
    msisdn_full: Mapped[str] = mapped_column(String(20), nullable=False)
    bdapps_subscriber_id: Mapped[str | None] = mapped_column(String(255))
    display_name: Mapped[str | None] = mapped_column(String(100))
    language_pref: Mapped[str] = mapped_column(
        Enum(UserLanguage, name="user_language", create_type=False),
        nullable=False,
        default=UserLanguage.BN,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    total_contributions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    sessions: Mapped[list[Session]] = relationship(back_populates="user", cascade="all, delete-orphan")
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User msisdn={self.msisdn}>"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    jwt_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    device_info: Mapped[dict | None] = mapped_column(JSONB)
    ip_address: Mapped[str | None] = mapped_column(INET)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped[User] = relationship(back_populates="sessions")

    __table_args__ = (
        Index("idx_sessions_user_id", "user_id"),
        Index("idx_sessions_expires", "expires_at", postgresql_where="NOT is_revoked"),
    )


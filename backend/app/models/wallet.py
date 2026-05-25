"""
GhoraGhuri — Wallet & Transaction Models
"""
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    DateTime, Enum, Float, Integer, String,
    CheckConstraint, ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TransactionType(str, enum.Enum):
    ROUTE_CHARGE = "route_charge"
    CONTRIBUTION_REWARD = "contribution_reward"
    AIRTIME_REDEMPTION = "airtime_redemption"
    BONUS = "bonus"
    REFUND = "refund"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    balance_coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_spent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_redeemed_bdt: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    last_transaction_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="wallet")
    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="wallet", cascade="all, delete-orphan", order_by="Transaction.created_at.desc()"
    )

    __table_args__ = (
        CheckConstraint("balance_coins >= 0", name="chk_balance_non_negative"),
    )

    def __repr__(self) -> str:
        return f"<Wallet user={self.user_id} coins={self.balance_coins}>"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=func.uuid_generate_v4()
    )
    wallet_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(
        Enum(TransactionType, name="transaction_type", create_type=False), nullable=False
    )
    amount_coins: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_bdt: Mapped[float | None] = mapped_column(Float)
    description_en: Mapped[str | None] = mapped_column(String(500))
    description_bn: Mapped[str | None] = mapped_column(String(500))
    reference_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    bdapps_trx_id: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        Enum(TransactionStatus, name="transaction_status", create_type=False),
        default=TransactionStatus.PENDING,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    wallet: Mapped[Wallet] = relationship(back_populates="transactions")

    __table_args__ = (
        Index("idx_transactions_wallet", "wallet_id", "created_at"),
        Index("idx_transactions_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Transaction {self.type} {self.amount_coins} coins>"


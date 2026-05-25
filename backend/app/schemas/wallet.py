"""
GhoraGhuri — Wallet Schemas
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WalletOut(BaseModel):
    """Wallet balance information."""
    balance_coins: int
    total_earned: int
    total_spent: int
    total_redeemed_bdt: float
    balance_bdt_equivalent: float  # computed: balance_coins * coin_to_bdt_rate


class TransactionOut(BaseModel):
    """Single transaction record."""
    id: str
    type: str
    amount_coins: int
    amount_bdt: float | None
    description_en: str | None
    description_bn: str | None
    status: str
    created_at: datetime


class RedeemRequestIn(BaseModel):
    """Redeem Jatri Coins for airtime."""
    coins: int = Field(..., ge=50, description="Minimum 50 coins to redeem")


class RedeemResultOut(BaseModel):
    """Redemption result."""
    coins_redeemed: int
    bdt_credited: float
    new_balance: int
    transaction_id: str

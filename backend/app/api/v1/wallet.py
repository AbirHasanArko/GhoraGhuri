"""
GhoraGhuri — Wallet API Endpoints
Balance, transaction history, coin redemption.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_language
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.wallet import Transaction, TransactionStatus, TransactionType, Wallet
from app.schemas.wallet import (
    RedeemRequestIn, RedeemResultOut,
    TransactionOut, WalletOut,
)
from app.utils.i18n import t

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("", response_model=WalletOut)
async def get_wallet(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current wallet balance and stats."""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = result.scalar_one_or_none()

    if not wallet:
        wallet = Wallet(user_id=user.id)
        db.add(wallet)
        await db.flush()

    return WalletOut(
        balance_coins=wallet.balance_coins,
        total_earned=wallet.total_earned,
        total_spent=wallet.total_spent,
        total_redeemed_bdt=wallet.total_redeemed_bdt,
        balance_bdt_equivalent=round(wallet.balance_coins * settings.coin_to_bdt_rate, 2),
    )


@router.get("/transactions", response_model=list[TransactionOut])
async def get_transactions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """Get paginated transaction history."""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = result.scalar_one_or_none()

    if not wallet:
        return []

    offset = (page - 1) * limit
    result = await db.execute(
        select(Transaction)
        .where(Transaction.wallet_id == wallet.id)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    transactions = result.scalars().all()

    return [
        TransactionOut(
            id=txn.id,
            type=txn.type,
            amount_coins=txn.amount_coins,
            amount_bdt=txn.amount_bdt,
            description_en=txn.description_en,
            description_bn=txn.description_bn,
            status=txn.status,
            created_at=txn.created_at,
        )
        for txn in transactions
    ]


@router.post("/redeem", response_model=RedeemResultOut)
async def redeem_coins(
    body: RedeemRequestIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """
    Redeem Jatri Coins for airtime credit.
    Minimum redemption: 50 coins.
    Rate: 10 coins = 1 BDT.
    """
    result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = result.scalar_one_or_none()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if body.coins < settings.min_redeem_coins:
        raise HTTPException(
            status_code=400,
            detail=t("min_redeem_error", lang, min=settings.min_redeem_coins),
        )

    if wallet.balance_coins < body.coins:
        raise HTTPException(
            status_code=400,
            detail=t("insufficient_balance", lang),
        )

    bdt_amount = round(body.coins * settings.coin_to_bdt_rate, 2)

    # Deduct coins
    wallet.balance_coins -= body.coins
    wallet.total_spent += body.coins
    wallet.total_redeemed_bdt += bdt_amount

    # Create transaction
    txn = Transaction(
        wallet_id=wallet.id,
        type=TransactionType.AIRTIME_REDEMPTION,
        amount_coins=-body.coins,
        amount_bdt=bdt_amount,
        description_en=f"Redeemed {body.coins} coins for ৳{bdt_amount} airtime",
        description_bn=f"{body.coins} কয়েন ৳{bdt_amount} এয়ারটাইমে রূপান্তরিত",
        status=TransactionStatus.COMPLETED,
    )
    db.add(txn)
    await db.flush()

    # TODO: In production, trigger actual airtime credit via bdapps CAAS
    logger.info(f"Redeemed {body.coins} coins → {bdt_amount} BDT for user {user.msisdn}")

    return RedeemResultOut(
        coins_redeemed=body.coins,
        bdt_credited=bdt_amount,
        new_balance=wallet.balance_coins,
        transaction_id=txn.id,
    )

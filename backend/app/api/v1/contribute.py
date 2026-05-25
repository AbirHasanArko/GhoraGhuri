"""
GhoraGhuri — Contribution API Endpoints
Crowd reports, route verification, GPS tracking.
"""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_language
from app.api.v1.routes import get_graph
from app.config import settings
from app.database import get_db
from app.models.contribution import Contribution, GpsTrack
from app.models.user import User
from app.models.wallet import Transaction, TransactionType, TransactionStatus, Wallet
from app.schemas.contribution import (
    ContributionOut, CrowdReportIn, GpsTrackCompleteIn,
    GpsTrackStartIn, RouteVerifyIn,
)
from app.utils.i18n import t

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contribute", tags=["Contributions"])


async def _award_coins(
    db: AsyncSession,
    user: User,
    contribution_id: str,
    coins: int,
    desc_en: str,
    desc_bn: str,
) -> None:
    """Award Jatri Coins to a contributor."""
    from sqlalchemy import select

    # Get wallet
    result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
    wallet = result.scalar_one_or_none()

    if not wallet:
        wallet = Wallet(user_id=user.id)
        db.add(wallet)
        await db.flush()

    wallet.balance_coins += coins
    wallet.total_earned += coins

    # Create transaction
    txn = Transaction(
        wallet_id=wallet.id,
        type=TransactionType.CONTRIBUTION_REWARD,
        amount_coins=coins,
        amount_bdt=coins * settings.coin_to_bdt_rate,
        description_en=desc_en,
        description_bn=desc_bn,
        reference_id=contribution_id,
        status=TransactionStatus.COMPLETED,
    )
    db.add(txn)

    # Update user stats
    user.total_contributions += 1


@router.post("/crowd-report", response_model=ContributionOut)
async def submit_crowd_report(
    body: CrowdReportIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """Submit a crowd level report for a transport stop or route."""
    coins = settings.reward_crowd_report

    # Create contribution
    contribution = Contribution(
        user_id=user.id,
        type="crowd_report",
        data_json={
            "crowd_level": body.crowd_level,
            "edge_id": body.edge_id,
            "node_code": body.node_code,
            "notes": body.notes,
        },
        related_edge_id=body.edge_id,
        reward_coins=coins,
        is_rewarded=True,
        validation_status="validated",  # auto-validate crowd reports
    )

    if body.lat and body.lng:
        from geoalchemy2.elements import WKTElement
        contribution.location = WKTElement(f"POINT({body.lng} {body.lat})", srid=4326)

    db.add(contribution)
    await db.flush()

    # Update graph in-memory if edge_id provided
    if body.edge_id:
        graph = get_graph()
        graph.update_edge_crowd(body.edge_id, body.crowd_level)

    # Award coins
    await _award_coins(
        db, user, contribution.id, coins,
        f"Crowd report submitted — {coins} Jatri Coins",
        f"ভিড় রিপোর্ট জমা — {coins} যাত্রী কয়েন",
    )

    return ContributionOut(
        contribution_id=contribution.id,
        type="crowd_report",
        reward_coins=coins,
        message=t("crowd_report_thanks", "en", coins=coins),
        message_bn=t("crowd_report_thanks", "bn", coins=coins),
    )


@router.post("/verify-route", response_model=ContributionOut)
async def verify_route(
    body: RouteVerifyIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """Verify or update transport route data."""
    coins = settings.reward_route_verify

    contribution = Contribution(
        user_id=user.id,
        type="route_verify",
        related_edge_id=body.edge_id,
        data_json={
            "is_active": body.is_active,
            "fare_bdt": body.fare_bdt,
            "time_minutes": body.time_minutes,
            "crowd_level": body.crowd_level,
            "notes": body.notes,
        },
        reward_coins=coins,
        is_rewarded=True,
        validation_status="validated",
    )
    db.add(contribution)
    await db.flush()

    await _award_coins(
        db, user, contribution.id, coins,
        f"Route verified — {coins} Jatri Coins",
        f"রুট যাচাই — {coins} যাত্রী কয়েন",
    )

    return ContributionOut(
        contribution_id=contribution.id,
        type="route_verify",
        reward_coins=coins,
        message=t("route_verify_thanks", "en", coins=coins),
        message_bn=t("route_verify_thanks", "bn", coins=coins),
    )


@router.post("/gps-track/start", response_model=ContributionOut)
async def start_gps_track(
    body: GpsTrackStartIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """Start a GPS tracking session."""
    contribution = Contribution(
        user_id=user.id,
        type="gps_track",
        data_json={"transport_mode": body.transport_mode},
        reward_coins=0,  # awarded on completion
        validation_status="pending",
    )
    db.add(contribution)
    await db.flush()

    gps_track = GpsTrack(
        contribution_id=contribution.id,
        user_id=user.id,
    )
    db.add(gps_track)

    return ContributionOut(
        contribution_id=contribution.id,
        type="gps_track",
        reward_coins=0,
        message="GPS tracking started. Points will be collected via WebSocket.",
        message_bn="জিপিএস ট্র্যাকিং শুরু হয়েছে।",
    )


@router.post("/gps-track/complete", response_model=ContributionOut)
async def complete_gps_track(
    body: GpsTrackCompleteIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """Complete a GPS tracking session and earn coins."""
    from sqlalchemy import select

    # Get contribution and GPS track
    result = await db.execute(
        select(Contribution).where(
            Contribution.id == body.contribution_id,
            Contribution.user_id == user.id,
        )
    )
    contribution = result.scalar_one_or_none()
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    result = await db.execute(
        select(GpsTrack).where(GpsTrack.contribution_id == body.contribution_id)
    )
    track = result.scalar_one_or_none()
    if not track:
        raise HTTPException(status_code=404, detail="GPS track not found")

    # Add final batch of points if provided
    if body.points:
        existing_points = track.points or []
        new_points = [p.model_dump() for p in body.points]
        track.points = existing_points + new_points
        track.total_points = len(track.points)

    track.is_complete = True

    # Calculate reward based on distance
    distance_km = track.distance_meters / 1000.0 if track.distance_meters > 0 else 0.5
    coins = max(int(distance_km * settings.reward_gps_track_per_km), 2)

    contribution.reward_coins = coins
    contribution.is_rewarded = True
    contribution.validation_status = "validated"

    await _award_coins(
        db, user, contribution.id, coins,
        f"GPS track ({distance_km:.1f} km) — {coins} Jatri Coins",
        f"জিপিএস ট্র্যাক ({distance_km:.1f} কিমি) — {coins} যাত্রী কয়েন",
    )

    return ContributionOut(
        contribution_id=contribution.id,
        type="gps_track",
        reward_coins=coins,
        message=t("gps_track_thanks", "en", coins=coins),
        message_bn=t("gps_track_thanks", "bn", coins=coins),
    )

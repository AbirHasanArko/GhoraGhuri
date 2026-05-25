"""
GhoraGhuri — Route Finding API Endpoints
Find multi-modal routes with A* algorithm + bdapps payment.
"""
from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_language
from app.config import settings
from app.database import get_db
from app.engine.astar import find_route
from app.engine.cost import RoutePreferences
from app.engine.graph import TransportGraph
from app.engine.seed_data import create_dhaka_graph
from app.models.user import User
from app.schemas.route import (
    RouteRequestIn, RouteResultOut, RouteStepOut,
)
from app.services.bdapps.caas import CaasService
from app.services.bdapps.client import BdAppsError
from app.utils.i18n import t

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/routes", tags=["Routes"])

# Graph is loaded once at startup (see main.py lifespan)
_graph: TransportGraph | None = None
caas_service = CaasService()


def get_graph() -> TransportGraph:
    """Get the loaded transport graph."""
    global _graph
    if _graph is None:
        _graph = create_dhaka_graph()
    return _graph


def set_graph(graph: TransportGraph) -> None:
    """Set the transport graph (called from startup)."""
    global _graph
    _graph = graph


@router.post("/find", response_model=RouteResultOut)
async def find_route_endpoint(
    body: RouteRequestIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    lang: str = Depends(get_language),
):
    """
    Find optimal multi-modal route.

    Flow:
    1. Resolve origin/destination to graph nodes
    2. Run A* routing engine
    3. Charge user via bdapps direct debit
    4. Return route result (only if payment succeeds)
    """
    graph = get_graph()

    # ── Resolve origin ────────────────────────────────────
    origin_id = None
    if body.origin:
        candidates = graph.find_nearest_node(body.origin.lat, body.origin.lng)
        origin_id = candidates[0] if candidates else None
    elif body.origin_text:
        origin_id = graph.find_node_by_name(body.origin_text, lang)

    if not origin_id:
        raise HTTPException(
            status_code=400,
            detail=t("route_not_found", lang) if lang == "bn"
            else "Could not resolve origin location",
        )

    # ── Resolve destination ───────────────────────────────
    dest_id = None
    if body.destination:
        candidates = graph.find_nearest_node(body.destination.lat, body.destination.lng)
        dest_id = candidates[0] if candidates else None
    elif body.destination_text:
        dest_id = graph.find_node_by_name(body.destination_text, lang)

    if not dest_id:
        raise HTTPException(
            status_code=400,
            detail=t("route_not_found", lang) if lang == "bn"
            else "Could not resolve destination location",
        )

    # ── Run A* routing ────────────────────────────────────
    preferences = RoutePreferences(optimize=body.optimize)
    result = find_route(graph, origin_id, dest_id, preferences)

    if not result.is_found:
        raise HTTPException(
            status_code=404,
            detail=result.error_message or t("route_not_found", lang),
        )

    # ── Charge user via bdapps ────────────────────────────
    route_id = str(uuid.uuid4())
    trx_id = None
    charge_bdt = settings.route_charge_bdt

    if settings.bdapps_configured and user.bdapps_subscriber_id:
        try:
            debit_result = await caas_service.direct_debit(
                subscriber_id=user.bdapps_subscriber_id,
                amount=charge_bdt,
            )

            if not debit_result.is_success:
                if debit_result.status_code == "E1326":
                    raise HTTPException(
                        status_code=402,
                        detail=t("insufficient_balance", lang),
                    )
                raise HTTPException(
                    status_code=402,
                    detail=t("payment_failed", lang),
                )

            trx_id = debit_result.external_trx_id
            logger.info(f"Charged {charge_bdt} BDT from user {user.msisdn} | trx={trx_id}")

        except BdAppsError as e:
            logger.error(f"Payment failed for user {user.msisdn}: {e}")
            raise HTTPException(
                status_code=402,
                detail=t("payment_failed", lang),
            )
    else:
        logger.info("bdapps not configured — skipping payment (dev mode)")

    # ── Build response ────────────────────────────────────
    steps = [
        RouteStepOut(
            step_order=step.step_order,
            from_name_en=step.from_node.name_en,
            from_name_bn=step.from_node.name_bn,
            to_name_en=step.to_node.name_en,
            to_name_bn=step.to_node.name_bn,
            transport_mode=step.transport_mode,
            instruction_en=step.instruction_en,
            instruction_bn=step.instruction_bn,
            duration_minutes=step.duration_minutes,
            fare_bdt=step.fare_bdt,
            distance_meters=step.distance_meters,
        )
        for step in result.steps
    ]

    return RouteResultOut(
        route_id=route_id,
        steps=steps,
        total_time_min=result.total_time_min,
        total_time_max=result.total_time_max,
        total_fare_min=result.total_fare_min,
        total_fare_max=result.total_fare_max,
        total_distance_meters=result.total_distance_meters,
        num_transfers=result.num_transfers,
        confidence_score=result.confidence_score,
        charge_bdt=charge_bdt,
        transaction_id=trx_id,
    )


@router.get("/nodes")
async def list_nodes(lang: str = Depends(get_language)):
    """List all available transport nodes (for autocomplete)."""
    graph = get_graph()

    nodes = []
    for node_id, node in graph.nodes.items():
        nodes.append({
            "id": node.id,
            "code": node.code,
            "name": node.name_bn if lang == "bn" else node.name_en,
            "name_en": node.name_en,
            "name_bn": node.name_bn,
            "type": node.node_type,
            "lat": node.lat,
            "lng": node.lng,
        })

    return {"nodes": sorted(nodes, key=lambda n: n["name"])}

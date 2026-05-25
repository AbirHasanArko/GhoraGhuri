"""
GhoraGhuri — SMS Fallback API Endpoints
Handles inbound SMS route requests from bdapps webhook.
"""
from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Request

from app.api.v1.routes import get_graph
from app.engine.astar import find_route
from app.engine.cost import RoutePreferences
from app.services.bdapps.client import BdAppsClient
from app.services.bdapps.sms import SmsService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sms", tags=["SMS Fallback"])

sms_service = SmsService()

# Pattern: "mirpur 10 to dhanmondi 27" or "মিরপুর ১০ থেকে ধানমন্ডি ২৭"
ROUTE_PATTERN_EN = re.compile(r"(.+?)\s+to\s+(.+)", re.IGNORECASE)
ROUTE_PATTERN_BN = re.compile(r"(.+?)\s+থেকে\s+(.+)")


@router.post("/receive")
async def receive_sms(request: Request):
    """
    Webhook endpoint for inbound SMS from bdapps.
    Parses route request, computes route, sends result back via SMS.
    """
    try:
        data = await request.json()
    except Exception:
        return {"statusCode": "S1000", "statusDetail": "Acknowledged"}

    parsed = SmsService.parse_receive_webhook(data)
    message = parsed.message.strip()
    source = parsed.source_address

    logger.info(f"SMS received from {source}: {message}")

    # Parse route request
    origin_text = None
    dest_text = None
    lang = "en"

    match = ROUTE_PATTERN_BN.match(message)
    if match:
        origin_text = match.group(1).strip()
        dest_text = match.group(2).strip()
        lang = "bn"
    else:
        match = ROUTE_PATTERN_EN.match(message)
        if match:
            origin_text = match.group(1).strip()
            dest_text = match.group(2).strip()

    if not origin_text or not dest_text:
        # Send help message
        try:
            await sms_service.send_sms(
                destination=source,
                message="GhoraGhuri: Send route request as 'Origin to Destination'. Example: 'Mirpur 10 to Dhanmondi 27'",
            )
        except Exception as e:
            logger.error(f"Failed to send help SMS: {e}")
        return {"statusCode": "S1000", "statusDetail": "Help sent"}

    # Find route
    graph = get_graph()
    origin_id = graph.find_node_by_name(origin_text, lang)
    dest_id = graph.find_node_by_name(dest_text, lang)

    if not origin_id or not dest_id:
        try:
            await sms_service.send_sms(
                destination=source,
                message=f"GhoraGhuri: Could not find route from '{origin_text}' to '{dest_text}'. Please check the location names.",
            )
        except Exception as e:
            logger.error(f"Failed to send error SMS: {e}")
        return {"statusCode": "S1000", "statusDetail": "Location not found"}

    # Run A* search
    result = find_route(graph, origin_id, dest_id, RoutePreferences())

    if not result.is_found:
        try:
            await sms_service.send_sms(
                destination=source,
                message=f"GhoraGhuri: No route found from '{origin_text}' to '{dest_text}'.",
            )
        except Exception as e:
            logger.error(f"Failed to send no-route SMS: {e}")
        return {"statusCode": "S1000", "statusDetail": "No route found"}

    # Format and send route result
    steps_data = [
        {
            "transport_mode": s.transport_mode,
            "instruction_en": s.instruction_en,
            "instruction_bn": s.instruction_bn,
        }
        for s in result.steps
    ]

    sms_text = SmsService.format_route_sms(
        steps=steps_data,
        total_time_min=result.total_time_min,
        total_time_max=result.total_time_max,
        total_fare_min=result.total_fare_min,
        total_fare_max=result.total_fare_max,
        lang=lang,
    )

    try:
        await sms_service.send_sms(destination=source, message=sms_text)
        logger.info(f"Route SMS sent to {source}")
    except Exception as e:
        logger.error(f"Failed to send route SMS: {e}")

    return {"statusCode": "S1000", "statusDetail": "Route sent"}

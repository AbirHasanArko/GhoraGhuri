"""
GhoraGhuri — bdapps Subscription Service
Handles /subscription/send, /subscription/query-base, /subscription/getStatus
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.services.bdapps.client import BdAppsClient

logger = logging.getLogger(__name__)


@dataclass
class SubscriptionResult:
    status_code: str
    status_detail: str
    subscription_status: str  # REGISTERED | UNREGISTERED


@dataclass
class BaseSizeResult:
    base_size: int
    status_code: str


class SubscriptionService:
    """
    bdapps Subscription management.

    Endpoints:
        POST /subscription/send      — Subscribe/unsubscribe user
        POST /subscription/query-base — Get total subscriber count
        POST /subscription/getStatus  — Check user subscription status
    """

    def __init__(self, client: BdAppsClient | None = None):
        self.client = client or BdAppsClient()

    async def subscribe(self, subscriber_id: str) -> SubscriptionResult:
        """Subscribe a user to the application."""
        payload = {
            "subscriberId": BdAppsClient.format_msisdn(subscriber_id),
            "action": "1",  # 1 = subscribe
        }
        response = await self.client._post("/subscription/send", payload)
        return SubscriptionResult(
            status_code=response.get("statusCode", ""),
            status_detail=response.get("statusDetail", ""),
            subscription_status=response.get("subscriptionStatus", ""),
        )

    async def unsubscribe(self, subscriber_id: str) -> SubscriptionResult:
        """Unsubscribe a user from the application."""
        payload = {
            "subscriberId": BdAppsClient.format_msisdn(subscriber_id),
            "action": "0",  # 0 = unsubscribe
        }
        response = await self.client._post("/subscription/send", payload)
        return SubscriptionResult(
            status_code=response.get("statusCode", ""),
            status_detail=response.get("statusDetail", ""),
            subscription_status=response.get("subscriptionStatus", ""),
        )

    async def get_status(self, subscriber_id: str) -> SubscriptionResult:
        """Check a user's subscription status."""
        payload = {
            "subscriberId": BdAppsClient.format_msisdn(subscriber_id),
        }
        response = await self.client._post("/subscription/getStatus", payload)
        return SubscriptionResult(
            status_code=response.get("statusCode", ""),
            status_detail=response.get("statusDetail", ""),
            subscription_status=response.get("subscriptionStatus", ""),
        )

    async def get_base_size(self) -> BaseSizeResult:
        """Get the total number of registered subscribers."""
        response = await self.client._post("/subscription/query-base", {})
        return BaseSizeResult(
            base_size=int(response.get("baseSize", 0)),
            status_code=response.get("statusCode", ""),
        )

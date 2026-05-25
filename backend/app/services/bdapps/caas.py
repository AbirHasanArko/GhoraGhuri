"""
GhoraGhuri — bdapps CAAS (Charging) Service
Handles /caas/direct/debit and /caas/get/balance API calls.

Used for:
- Charging users for route queries (direct debit)
- Checking subscriber balance before charging
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from app.services.bdapps.client import BdAppsClient

logger = logging.getLogger(__name__)


@dataclass
class BalanceResult:
    """Result of a balance query."""
    account_type: str  # 'Pre Paid' | 'Post paid'
    account_status: str  # 'Active' | 'Disable'
    chargeable_balance: float
    status_code: str


@dataclass
class DebitResult:
    """Result of a direct debit charge."""
    external_trx_id: str
    internal_trx_id: str
    reference_id: str
    timestamp: str
    status_code: str
    status_detail: str
    is_success: bool


class CaasService:
    """
    bdapps Charging-as-a-Service (CAAS).

    Endpoints:
        POST /caas/get/balance  — Query subscriber balance
        POST /caas/direct/debit — Charge subscriber's mobile account
    """

    def __init__(self, client: BdAppsClient | None = None):
        self.client = client or BdAppsClient()

    async def get_balance(self, subscriber_id: str) -> BalanceResult:
        """
        Query the balance of a subscriber's mobile account.

        Args:
            subscriber_id: The masked subscriber ID from OTP verification,
                          or MSISDN in local format

        Returns:
            BalanceResult with account type, status, and chargeable balance

        Raises:
            BdAppsError: On API failure
        """
        # subscriber_id for CAAS does NOT use tel: prefix (unlike OTP)
        if subscriber_id.startswith("tel:"):
            subscriber_id = subscriber_id[4:]

        payload = {
            "subscriberId": subscriber_id,
            "paymentInstrumentName": "MobileAccount",
        }

        logger.info(f"Querying balance for subscriber {subscriber_id[:8]}***")
        response = await self.client._post("/caas/get/balance", payload)

        return BalanceResult(
            account_type=response.get("accountType", ""),
            account_status=response.get("accountStatus", ""),
            chargeable_balance=float(response.get("chargeableBalance", 0)),
            status_code=response.get("statusCode", "S1000"),
        )

    async def direct_debit(
        self,
        subscriber_id: str,
        amount: float,
        external_trx_id: str | None = None,
    ) -> DebitResult:
        """
        Charge a specific amount from a subscriber's mobile account.

        This is called BEFORE returning a route result to the user.
        If the charge fails, the route result should NOT be returned.

        Args:
            subscriber_id: The masked subscriber ID from OTP verification
            amount: Amount in BDT to charge (e.g., 2.0)
            external_trx_id: Optional external transaction ID for idempotency.
                            Auto-generated if not provided.

        Returns:
            DebitResult with transaction details and success flag

        Raises:
            BdAppsError:
                E1326 = Insufficient balance
                E1328 = Charging operation not allowed
                E1337 = Duplicate request
        """
        if external_trx_id is None:
            external_trx_id = uuid.uuid4().hex

        # subscriber_id for CAAS does NOT use tel: prefix
        if subscriber_id.startswith("tel:"):
            subscriber_id = subscriber_id[4:]

        payload = {
            "subscriberId": subscriber_id,
            "paymentInstrumentName": "MobileAccount",
            "currency": "BDT",
            "amount": str(amount),
            "externalTrxId": external_trx_id,
        }

        logger.info(
            f"Direct debit {amount} BDT from subscriber {subscriber_id[:8]}*** "
            f"| trx={external_trx_id}"
        )

        try:
            response = await self.client._post("/caas/direct/debit", payload)
            return DebitResult(
                external_trx_id=external_trx_id,
                internal_trx_id=response.get("internalTrxId", ""),
                reference_id=str(response.get("referenceId", "")),
                timestamp=response.get("timeStamp", ""),
                status_code=response.get("statusCode", "S1000"),
                status_detail=response.get("statusDetail", "Success"),
                is_success=True,
            )
        except Exception as e:
            logger.error(f"Direct debit failed for {subscriber_id[:8]}***: {e}")
            return DebitResult(
                external_trx_id=external_trx_id,
                internal_trx_id="",
                reference_id="",
                timestamp="",
                status_code=getattr(e, "status_code", "E_UNKNOWN"),
                status_detail=str(e),
                is_success=False,
            )

"""
GhoraGhuri — bdapps SMS Service
Handles /sms/send and /sms/receive for offline route requests.

SMS Fallback Flow:
1. User sends SMS to shortcode: "Mirpur 10 to Dhanmondi 27"
2. bdapps delivers to our webhook (/sms/receive)
3. We parse the route request, compute route, charge user
4. We send result back via /sms/send
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.services.bdapps.client import BdAppsClient

logger = logging.getLogger(__name__)


@dataclass
class SmsSendResult:
    """Result of sending an SMS."""
    request_id: str
    status_code: str
    status_detail: str
    destination_responses: list[dict]


@dataclass
class SmsReceivePayload:
    """Parsed inbound SMS from bdapps webhook."""
    source_address: str  # tel:880XXXXXXXXXX
    message: str
    request_id: str
    application_id: str
    encoding: str


class SmsService:
    """
    bdapps SMS send/receive service.

    Endpoints:
        POST /sms/send    — Send SMS to subscriber(s)
        POST /sms/receive — Webhook: receive inbound SMS
    """

    def __init__(self, client: BdAppsClient | None = None):
        self.client = client or BdAppsClient()

    async def send_sms(
        self,
        destination: str | list[str],
        message: str,
        source_address: str | None = None,
        delivery_report: bool = False,
    ) -> SmsSendResult:
        """
        Send an SMS to one or more subscribers.

        Args:
            destination: Phone number(s) — string or list of strings
            message: SMS content (max ~160 chars for single SMS)
            source_address: Optional source address/shortcode
            delivery_report: Whether to request delivery confirmation

        Returns:
            SmsSendResult with per-destination status

        Raises:
            BdAppsError: On API failure
        """
        if isinstance(destination, str):
            destination = [destination]

        # Format all numbers to tel: format
        formatted_destinations = [
            BdAppsClient.format_msisdn(d) for d in destination
        ]

        payload = {
            "version": "1.0",
            "message": message,
            "destinationAddresses": formatted_destinations,
            "deliveryStatusRequest": "1" if delivery_report else "0",
            "encoding": "0",  # text encoding
        }

        if source_address:
            payload["sourceAddress"] = source_address

        logger.info(f"Sending SMS to {len(formatted_destinations)} recipient(s)")
        response = await self.client._post("/sms/send", payload)

        return SmsSendResult(
            request_id=response.get("requestId", ""),
            status_code=response.get("statusCode", "S1000"),
            status_detail=response.get("statusDetail", ""),
            destination_responses=response.get("destinationResponses", []),
        )

    @staticmethod
    def parse_receive_webhook(data: dict) -> SmsReceivePayload:
        """
        Parse an inbound SMS webhook payload from bdapps.

        bdapps sends POST to our webhook URL with the SMS data.

        Args:
            data: The JSON body from bdapps /sms/receive webhook

        Returns:
            SmsReceivePayload with parsed fields
        """
        return SmsReceivePayload(
            source_address=data.get("sourceAddress", ""),
            message=data.get("message", ""),
            request_id=data.get("requestId", ""),
            application_id=data.get("applicationId", ""),
            encoding=data.get("encoding", "0"),
        )

    @staticmethod
    def format_route_sms(
        steps: list[dict],
        total_time_min: float,
        total_time_max: float,
        total_fare_min: float,
        total_fare_max: float,
        lang: str = "bn",
    ) -> str:
        """
        Format a route result as an SMS-friendly text message.

        Must fit within SMS limits (~480 chars for concatenated SMS).

        Args:
            steps: List of route step dicts
            total_time_min/max: Time range in minutes
            total_fare_min/max: Fare range in BDT
            lang: 'en' or 'bn'

        Returns:
            Formatted SMS string
        """
        if lang == "bn":
            header = f"ঘোরাঘুরি রুট:\nসময়: {int(total_time_min)}-{int(total_time_max)} মিনিট\nখরচ: ৳{int(total_fare_min)}-{int(total_fare_max)}\n\n"
            step_lines = []
            for i, step in enumerate(steps, 1):
                mode = step.get("transport_mode", "")
                instruction = step.get("instruction_bn", step.get("instruction_en", ""))
                step_lines.append(f"{i}. {instruction}")
        else:
            header = f"GhoraGhuri Route:\nTime: {int(total_time_min)}-{int(total_time_max)} min\nFare: Tk {int(total_fare_min)}-{int(total_fare_max)}\n\n"
            step_lines = []
            for i, step in enumerate(steps, 1):
                instruction = step.get("instruction_en", "")
                step_lines.append(f"{i}. {instruction}")

        result = header + "\n".join(step_lines)

        # Truncate if too long for SMS
        if len(result) > 450:
            result = result[:447] + "..."

        return result

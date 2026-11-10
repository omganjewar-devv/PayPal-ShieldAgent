import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger


class PayPalClient:
    """
    Client for interacting with the PayPal Disputes REST API.
    Supports both Sandbox live calls and Mock responses for local testing.
    """
    def __init__(self):
        self.base_url = settings.paypal_base_url
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def get_access_token(self) -> str:
        """Fetch OAuth2 Bearer token from PayPal Sandbox"""
        if self._access_token:
            return self._access_token

        if self.client_id == "mock_client_id":
            return "mock_sandbox_access_token"

        url = f"{self.base_url}/v1/oauth2/token"
        headers = {"Accept": "application/json", "Accept-Language": "en_US"}
        data = {"grant_type": "client_credentials"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, auth=(self.client_id, self.client_secret), headers=headers, data=data
            )
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data.get("access_token")
            return self._access_token

    async def get_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """Fetch full dispute details from /v1/customer/disputes/{id}"""
        if self.client_id == "mock_client_id":
            logger.info(f"[MOCK] Fetching dispute details for {dispute_id}")
            return self._get_mock_dispute(dispute_id)

        token = await self.get_access_token()
        url = f"{self.base_url}/v1/customer/disputes/{dispute_id}"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def provide_evidence(self, dispute_id: str, evidence_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit representment evidence to /v1/customer/disputes/{id}/provide-evidence"""
        if self.client_id == "mock_client_id":
            logger.info(f"[MOCK] Autonomously submitting evidence to PayPal for {dispute_id}")
            return {
                "status": "SUCCESS",
                "dispute_id": dispute_id,
                "submitted_at": datetime.utcnow().isoformat(),
                "action": "EVIDENCE_SUBMITTED"
            }

        token = await self.get_access_token()
        url = f"{self.base_url}/v1/customer/disputes/{dispute_id}/provide-evidence"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=evidence_payload)
            response.raise_for_status()
            return response.json()

    async def accept_claim(self, dispute_id: str, reason: str = "AUTO_CONCEDE_LOW_ROI") -> Dict[str, Any]:
        """Accept dispute liability / refund buyer to avoid dispute fee"""
        if self.client_id == "mock_client_id":
            logger.info(f"[MOCK] Accepting claim for {dispute_id} (Reason: {reason})")
            return {
                "status": "ACCEPTED",
                "dispute_id": dispute_id,
                "reason": reason
            }

        token = await self.get_access_token()
        url = f"{self.base_url}/v1/customer/disputes/{dispute_id}/accept-claim"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json={"reason": reason})
            response.raise_for_status()
            return response.json()

    def _get_mock_dispute(self, dispute_id: str) -> Dict[str, Any]:
        return {
            "dispute_id": dispute_id,
            "create_time": "2026-11-10T10:00:00Z",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "status": "WAITING_FOR_SELLER_RESPONSE",
            "dispute_amount": {"currency_code": "USD", "value": "129.99"},
            "dispute_life_cycle_stage": "CHARGEBACK",
            "seller_response_due_date": "2026-11-17T12:00:00Z",
            "disputed_transactions": [
                {
                    "seller_transaction_id": "TXN-984729104",
                    "gross_amount": {"currency_code": "USD", "value": "129.99"},
                    "buyer": {"name": "Alex Mercer", "email": "alex.mercer@example.com"}
                }
            ]
        }


paypal_client = PayPalClient()

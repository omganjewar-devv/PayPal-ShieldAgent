from fastapi import APIRouter, Request, Header, HTTPException, status
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.logging import logger
from app.models.dispute import Dispute, DisputeReason, DisputeStatus, DisputeLifeCycleStage, DisputedTransaction, Money
from app.agents.orchestrator import shield_orchestrator

router = APIRouter(prefix="/webhooks", tags=["PayPal Webhooks"])


@router.post("/paypal")
async def handle_paypal_webhook(
    request: Request,
    paypal_auth_algo: Optional[str] = Header(None, alias="PAYPAL-AUTH-ALGO"),
    paypal_transmission_id: Optional[str] = Header(None, alias="PAYPAL-TRANSMISSION-ID")
):
    """
    Ingests inbound PayPal Dispute Webhooks (e.g. CUSTOMER.DISPUTE.CREATED).
    Triggers the ShieldAgent autonomous defense council.
    """
    payload = await request.json()
    event_type = payload.get("event_type")
    logger.info(f"Received PayPal Webhook Event: {event_type}")

    if event_type in ["CUSTOMER.DISPUTE.CREATED", "CUSTOMER.DISPUTE.UPDATED"]:
        resource = payload.get("resource", {})
        dispute_id = resource.get("dispute_id", "MOCK_DISPUTE")
        
        # Parse basic dispute details
        dispute = Dispute(
            dispute_id=dispute_id,
            create_time=datetime.utcnow(),
            disputed_transactions=[
                DisputedTransaction(
                    transaction_id=resource.get("disputed_transactions", [{}])[0].get("seller_transaction_id", "TXN-1234"),
                    gross_amount=Money(value=resource.get("dispute_amount", {}).get("value", "100.00")),
                    create_time=datetime.utcnow()
                )
            ],
            reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
            status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
            dispute_amount=Money(value=resource.get("dispute_amount", {}).get("value", "100.00")),
            dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK,
            raw_payload=payload
        )

        # Trigger autonomous defense pipeline
        dossier = await shield_orchestrator.defend_dispute(dispute, force_auto_submit=False)
        return {"status": "SUCCESS", "event": event_type, "dossier": dossier}

    return {"status": "IGNORED", "event": event_type}

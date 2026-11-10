from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.paypal_client import paypal_client
from app.agents.orchestrator import shield_orchestrator
from app.models.dispute import Dispute, DisputeReason, DisputeStatus, DisputeLifeCycleStage, DisputedTransaction, Money
from datetime import datetime

router = APIRouter(prefix="/disputes", tags=["Disputes Management"])


@router.get("/{dispute_id}")
async def get_dispute(dispute_id: str):
    """Fetch raw dispute details from PayPal sandbox or cache"""
    try:
        data = await paypal_client.get_dispute(dispute_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{dispute_id}/defend")
async def trigger_defense(dispute_id: str, auto_submit: bool = Query(False)):
    """Run ShieldAgent defense council on a given dispute ID"""
    try:
        raw_dispute = await paypal_client.get_dispute(dispute_id)
        
        dispute = Dispute(
            dispute_id=dispute_id,
            create_time=datetime.utcnow(),
            disputed_transactions=[
                DisputedTransaction(
                    transaction_id="TXN-DEFAULT",
                    gross_amount=Money(value=raw_dispute.get("dispute_amount", {}).get("value", "100.00")),
                    create_time=datetime.utcnow()
                )
            ],
            reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
            status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
            dispute_amount=Money(value=raw_dispute.get("dispute_amount", {}).get("value", "100.00")),
            dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK
        )

        dossier = await shield_orchestrator.defend_dispute(dispute, force_auto_submit=auto_submit)
        return {"dispute_id": dispute_id, "dossier": dossier}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

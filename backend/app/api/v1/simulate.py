from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime, timedelta
from app.models.dispute import (
    Dispute, DisputeReason, DisputeStatus, DisputeLifeCycleStage, DisputedTransaction, Money, BuyerInfo, CardScheme
)
from app.models.evidence import EvidencePackage, TrackingInfo, HistoricalTransaction, ImageForensicResult
from app.agents.orchestrator import shield_orchestrator

router = APIRouter(prefix="/simulate", tags=["Dispute Simulations"])


@router.post("/friendly-fraud-inr")
async def simulate_inr_friendly_fraud(auto_submit: bool = False):
    """
    Scenario 1: Customer claims 'Item Not Received' (INR).
    Evidence shows verified carrier tracking delivered to buyer's zip with signature.
    """
    dispute = Dispute(
        dispute_id="PP-D-83921",
        create_time=datetime.utcnow() - timedelta(hours=6),
        disputed_transactions=[
            DisputedTransaction(
                transaction_id="TXN-984712948",
                order_id="ORD-44910",
                gross_amount=Money(value="149.99"),
                create_time=datetime.utcnow() - timedelta(days=5)
            )
        ],
        reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
        status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
        dispute_amount=Money(value="149.99"),
        dispute_life_cycle_stage=DisputeLifeCycleStage.MERCHANT_REPRESENTMENT,
        scheme=CardScheme.VISA,
        scheme_reason_code="13.1",
        buyer_info=BuyerInfo(
            name="John Doe",
            email="john.doe@example.com",
            ip_address="198.51.100.42",
            shipping_address={"line1": "742 Evergreen Terrace", "postal_code": "94107", "city": "San Francisco"}
        ),
        seller_response_due_date=datetime.utcnow() + timedelta(days=7)
    )

    evidence = EvidencePackage(
        dispute_id=dispute.dispute_id,
        tracking_proofs=[
            TrackingInfo(
                carrier_name="USPS",
                tracking_number="9400111899562537628192",
                status="DELIVERED",
                delivery_postal_code="94107",
                delivery_signature_name="J. DOE",
                delivery_date=datetime.utcnow() - timedelta(days=2)
            )
        ]
    )

    dossier = await shield_orchestrator.defend_dispute(dispute, evidence, force_auto_submit=auto_submit)
    return {"scenario": "Friendly Fraud (INR)", "dispute": dispute, "dossier": dossier}


@router.post("/visa-ce30-liability-shift")
async def simulate_visa_ce30(auto_submit: bool = False):
    """
    Scenario 2: Customer claims 'Unauthorized Transaction' (Card Fraud).
    Merchant database contains 2 prior settled transactions 150 & 220 days ago
    with matching IP and postal code. Triggers Visa CE 3.0 automatic liability shift!
    """
    dispute = Dispute(
        dispute_id="PP-D-99104",
        create_time=datetime.utcnow() - timedelta(hours=2),
        disputed_transactions=[
            DisputedTransaction(
                transaction_id="TXN-110294819",
                order_id="ORD-88201",
                gross_amount=Money(value="320.00"),
                create_time=datetime.utcnow() - timedelta(days=3)
            )
        ],
        reason=DisputeReason.UNAUTHORISED,
        status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
        dispute_amount=Money(value="320.00"),
        dispute_life_cycle_stage=DisputeLifeCycleStage.MERCHANT_REPRESENTMENT,
        scheme=CardScheme.VISA,
        scheme_reason_code="10.4",
        buyer_info=BuyerInfo(
            name="Sarah Jenkins",
            email="sarah.j@example.com",
            ip_address="203.0.113.195",
            shipping_address={"postal_code": "10001", "city": "New York"}
        ),
        seller_response_due_date=datetime.utcnow() + timedelta(days=8)
    )

    evidence = EvidencePackage(
        dispute_id=dispute.dispute_id,
        ce30_qualifying_transactions=[
            HistoricalTransaction(
                transaction_id="TXN-HIST-01",
                timestamp=datetime.utcnow() - timedelta(days=140),
                amount=85.00,
                ip_address="203.0.113.195",
                shipping_postal_code="10001",
                card_fingerprint="card_9921",
                was_disputed=False
            ),
            HistoricalTransaction(
                transaction_id="TXN-HIST-02",
                timestamp=datetime.utcnow() - timedelta(days=210),
                amount=120.00,
                ip_address="203.0.113.195",
                shipping_postal_code="10001",
                card_fingerprint="card_9921",
                was_disputed=False
            )
        ]
    )

    dossier = await shield_orchestrator.defend_dispute(dispute, evidence, force_auto_submit=auto_submit)
    return {"scenario": "Visa CE 3.0 Liability Shift", "dispute": dispute, "dossier": dossier}


@router.post("/mastercard-missing-contact")
async def simulate_mastercard_missing_contact(auto_submit: bool = False):
    """
    Scenario 3 (From Barclays Research): Cardholder filed chargeback via Mastercard
    without attempting resolution with the merchant first.
    System flags procedural defect under Mastercard scheme rules.
    """
    dispute = Dispute(
        dispute_id="PP-D-77218",
        create_time=datetime.utcnow() - timedelta(hours=4),
        disputed_transactions=[
            DisputedTransaction(
                transaction_id="TXN-MC-8819",
                gross_amount=Money(value="189.50"),
                create_time=datetime.utcnow() - timedelta(days=7)
            )
        ],
        reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED,
        status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
        dispute_amount=Money(value="189.50"),
        dispute_life_cycle_stage=DisputeLifeCycleStage.MERCHANT_REPRESENTMENT,
        scheme=CardScheme.MASTERCARD,
        scheme_reason_code="4853",
        buyer_contacted_merchant=False,  # Procedural defect!
        seller_response_due_date=datetime.utcnow() + timedelta(days=5)
    )

    dossier = await shield_orchestrator.defend_dispute(dispute, None, force_auto_submit=auto_submit)
    return {"scenario": "Mastercard Missing Contact Defect", "dispute": dispute, "dossier": dossier}


@router.post("/scheme-arbitration-risk")
async def simulate_scheme_arbitration_risk(auto_submit: bool = False):
    """
    Scenario 4 (From Barclays Stage 9 Research): Dispute reaches Scheme Arbitration stage.
    Dispute is for $75. Loser faces a $500 scheme arbitration fee.
    Triage calculates negative EV and recommends CONCEDE_ARBITRATION to save $500!
    """
    dispute = Dispute(
        dispute_id="PP-D-55102",
        create_time=datetime.utcnow() - timedelta(days=35),
        disputed_transactions=[
            DisputedTransaction(
                transaction_id="TXN-ARB-11",
                gross_amount=Money(value="75.00"),
                create_time=datetime.utcnow() - timedelta(days=40)
            )
        ],
        reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED,
        status=DisputeStatus.UNDER_REVIEW,
        dispute_amount=Money(value="75.00"),
        dispute_life_cycle_stage=DisputeLifeCycleStage.SCHEME_ARBITRATION,
        scheme=CardScheme.VISA,
        scheme_reason_code="13.3",
        seller_response_due_date=datetime.utcnow() + timedelta(hours=18)  # Critical Day N-1 window!
    )

    dossier = await shield_orchestrator.defend_dispute(dispute, None, force_auto_submit=auto_submit)
    return {"scenario": "Scheme Arbitration Risk Triage", "dispute": dispute, "dossier": dossier}

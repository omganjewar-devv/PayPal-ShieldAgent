import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.dispute import (
    Dispute, DisputeReason, DisputeStatus, DisputeLifeCycleStage, DisputedTransaction, Money, BuyerInfo, CardScheme
)
from app.models.evidence import EvidencePackage, TrackingInfo, HistoricalTransaction
from app.agents.orchestrator import shield_orchestrator
from app.models.agent_response import DefenseAction


async def run_tests():
    print("\n--- Running Test 1: Friendly Fraud INR (Delivery Confirmed) ---")
    dispute_inr = Dispute(
        dispute_id="TEST-INR-01",
        create_time=datetime.utcnow(),
        disputed_transactions=[
            DisputedTransaction(
                transaction_id="TXN-001",
                gross_amount=Money(value="149.00"),
                create_time=datetime.utcnow()
            )
        ],
        reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
        status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
        dispute_amount=Money(value="149.00"),
        dispute_life_cycle_stage=DisputeLifeCycleStage.MERCHANT_REPRESENTMENT,
        scheme=CardScheme.VISA,
        buyer_info=BuyerInfo(
            shipping_address={"postal_code": "94107"}
        )
    )
    evidence_inr = EvidencePackage(
        dispute_id="TEST-INR-01",
        tracking_proofs=[
            TrackingInfo(
                carrier_name="USPS",
                tracking_number="9400111899562537628192",
                status="DELIVERED",
                delivery_postal_code="94107",
                delivery_date=datetime.utcnow() - timedelta(days=1)
            )
        ]
    )
    dossier_inr = await shield_orchestrator.defend_dispute(dispute_inr, evidence_inr)
    assert dossier_inr.triage.recommended_action == DefenseAction.DEFEND
    assert dossier_inr.forensics.pod_verified is True
    print(f"✓ Test 1 Passed: Win Probability = {dossier_inr.triage.win_probability}%")

    print("\n--- Running Test 2: Visa CE 3.0 Liability Shift ---")
    dispute_ce30 = Dispute(
        dispute_id="TEST-CE30-01",
        create_time=datetime.utcnow(),
        disputed_transactions=[
            DisputedTransaction(
                transaction_id="TXN-002",
                gross_amount=Money(value="250.00"),
                create_time=datetime.utcnow()
            )
        ],
        reason=DisputeReason.UNAUTHORISED,
        status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
        dispute_amount=Money(value="250.00"),
        dispute_life_cycle_stage=DisputeLifeCycleStage.MERCHANT_REPRESENTMENT,
        scheme=CardScheme.VISA,
        scheme_reason_code="10.4",
        buyer_info=BuyerInfo(
            ip_address="192.0.2.1"
        )
    )
    evidence_ce30 = EvidencePackage(
        dispute_id="TEST-CE30-01",
        ce30_qualifying_transactions=[
            HistoricalTransaction(
                transaction_id="TXN-H1",
                timestamp=datetime.utcnow() - timedelta(days=150),
                amount=50.0,
                ip_address="192.0.2.1",
                card_fingerprint="card_1"
            ),
            HistoricalTransaction(
                transaction_id="TXN-H2",
                timestamp=datetime.utcnow() - timedelta(days=200),
                amount=75.0,
                ip_address="192.0.2.1",
                card_fingerprint="card_1"
            )
        ]
    )
    dossier_ce30 = await shield_orchestrator.defend_dispute(dispute_ce30, evidence_ce30)
    assert dossier_ce30.compliance.visa_ce30_eligible is True
    assert dossier_ce30.compliance.liability_shift_guaranteed is True
    assert dossier_ce30.triage.win_probability == 98.0
    print(f"✓ Test 2 Passed: CE 3.0 Qualified = {dossier_ce30.compliance.visa_ce30_eligible}")

    print("\n--- Running Test 3: Mastercard Prior Contact Rule Violation (Barclays Flow) ---")
    dispute_mc = Dispute(
        dispute_id="TEST-MC-01",
        create_time=datetime.utcnow(),
        disputed_transactions=[
            DisputedTransaction(
                transaction_id="TXN-MC-01",
                gross_amount=Money(value="180.00"),
                create_time=datetime.utcnow()
            )
        ],
        reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED,
        status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
        dispute_amount=Money(value="180.00"),
        dispute_life_cycle_stage=DisputeLifeCycleStage.MERCHANT_REPRESENTMENT,
        scheme=CardScheme.MASTERCARD,
        scheme_reason_code="4853",
        buyer_contacted_merchant=False  # Violation
    )
    dossier_mc = await shield_orchestrator.defend_dispute(dispute_mc)
    assert dossier_mc.compliance.procedural_defect_identified is True
    assert dossier_mc.triage.recommended_action == DefenseAction.DEFEND
    print(f"✓ Test 3 Passed: Procedural Defect Caught = {dossier_mc.compliance.procedural_defect_identified}")

    print("\n--- Running Test 4: Scheme Arbitration Risk & Day N-1 Critical Alert ---")
    dispute_arb = Dispute(
        dispute_id="TEST-ARB-01",
        create_time=datetime.utcnow() - timedelta(days=30),
        disputed_transactions=[
            DisputedTransaction(
                transaction_id="TXN-ARB-01",
                gross_amount=Money(value="60.00"),
                create_time=datetime.utcnow() - timedelta(days=35)
            )
        ],
        reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED,
        status=DisputeStatus.UNDER_REVIEW,
        dispute_amount=Money(value="60.00"),
        dispute_life_cycle_stage=DisputeLifeCycleStage.SCHEME_ARBITRATION,
        scheme=CardScheme.VISA,
        seller_response_due_date=datetime.utcnow() + timedelta(hours=12)  # Day N-1!
    )
    dossier_arb = await shield_orchestrator.defend_dispute(dispute_arb)
    assert dossier_arb.triage.sla_urgency_tier == "CRITICAL_DAY_N_MINUS_1"
    assert dossier_arb.triage.recommended_action == DefenseAction.CONCEDE_ARBITRATION
    assert dossier_arb.triage.arbitration_risk.go_decision is False
    print(f"✓ Test 4 Passed: Action = {dossier_arb.triage.recommended_action}, SLA = {dossier_arb.triage.sla_urgency_tier}")

    print("\nAll 4 Core Defense & Scheme Compliance Tests Passed Successfully! 🚀")


if __name__ == "__main__":
    asyncio.run(run_tests())

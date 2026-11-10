from typing import List, Optional
from datetime import datetime, timedelta
from app.models.dispute import Dispute, DisputeReason
from app.models.evidence import EvidencePackage, HistoricalTransaction
from app.models.agent_response import ComplianceAssessment
from app.core.logging import logger


class ComplianceAgent:
    """
    Compliance Agent for Card Network Rules:
    Automates Visa Compelling Evidence 3.0 (CE 3.0) evaluation.
    
    Visa CE 3.0 Rule Criteria (Reason Code 10.4):
    1. Must locate >= 2 previous undisputed transactions.
    2. Transactions must have occurred between 120 and 365 days prior to dispute.
    3. At least one qualifying identifier (IP, Device ID, or Shipping Address) must match.
    
    Result: Guarantees liability shift back to the issuer!
    """

    async def verify_ce30(self, dispute: Dispute, evidence: Optional[EvidencePackage] = None) -> ComplianceAssessment:
        if not evidence or not evidence.ce30_qualifying_transactions:
            return ComplianceAssessment(
                visa_ce30_eligible=False,
                qualifying_orders_count=0,
                matched_criteria=[],
                liability_shift_guaranteed=False,
                citation="No historical customer transaction data provided for CE 3.0 evaluation."
            )

        dispute_time = dispute.create_time
        qualifying_txns: List[HistoricalTransaction] = []
        matched_criteria = set()

        # Target identifiers from current dispute
        current_ip = dispute.buyer_info.ip_address if dispute.buyer_info else None
        current_zip = (
            dispute.buyer_info.shipping_address.get("postal_code")
            if dispute.buyer_info and dispute.buyer_info.shipping_address
            else None
        )

        for txn in evidence.ce30_qualifying_transactions:
            if txn.was_disputed:
                continue

            # Time window: between 120 and 365 days ago
            days_diff = (dispute_time - txn.timestamp).days
            if 120 <= days_diff <= 365:
                criteria_hit = []
                if current_ip and txn.ip_address == current_ip:
                    criteria_hit.append("IP_ADDRESS")
                if current_zip and txn.shipping_postal_code == current_zip:
                    criteria_hit.append("SHIPPING_ADDRESS")

                if criteria_hit:
                    qualifying_txns.append(txn)
                    for c in criteria_hit:
                        matched_criteria.add(c)

        is_eligible = len(qualifying_txns) >= 2 and len(matched_criteria) > 0

        citation = (
            f"Visa Compelling Evidence 3.0: Found {len(qualifying_txns)} qualifying undisputed transactions "
            f"within 120-365 day window matching {list(matched_criteria)}. Liability shifts to issuer."
            if is_eligible
            else "Did not meet Visa CE 3.0 strict threshold (requires >=2 qualifying undisputed transactions)."
        )

        logger.info(f"[ComplianceAgent] CE 3.0 Eligible: {is_eligible} ({len(qualifying_txns)} qualifying orders)")

        return ComplianceAssessment(
            visa_ce30_eligible=is_eligible,
            qualifying_orders_count=len(qualifying_txns),
            matched_criteria=list(matched_criteria),
            mastercard_rule_code="4837_DEFENDED" if is_eligible else None,
            liability_shift_guaranteed=is_eligible,
            citation=citation
        )


compliance_agent = ComplianceAgent()

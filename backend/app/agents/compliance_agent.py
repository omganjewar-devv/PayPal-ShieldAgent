from typing import List, Optional
from datetime import datetime, timedelta
from app.models.dispute import Dispute, DisputeReason, CardScheme
from app.models.evidence import EvidencePackage, HistoricalTransaction
from app.models.agent_response import ComplianceAssessment
from app.core.logging import logger


class ComplianceAgent:
    """
    Card Scheme Compliance Engine:
    - Automates Visa Compelling Evidence 3.0 (CE 3.0) qualification.
    - Automates Mastercard Scheme Rules (e.g. Mandatory Prior Merchant Contact verification).
    - Detects procedural defects in issuer submissions (Barclays / Scheme rules).
    """

    async def verify_compliance(self, dispute: Dispute, evidence: Optional[EvidencePackage] = None) -> ComplianceAssessment:
        citations: List[str] = []
        procedural_defect = False
        mastercard_contact_verified = True

        # Rule Check 1: Mastercard Scheme Rule - Mandatory Cardholder-Merchant Contact
        # Under Mastercard rules (Reason Codes 4853, 4837), cardholders must attempt
        # direct contact with merchant prior to chargeback initiation.
        if dispute.scheme == CardScheme.MASTERCARD:
            if dispute.buyer_contacted_merchant is False:
                procedural_defect = True
                mastercard_contact_verified = False
                citations.append(
                    "Mastercard Dispute Rules Violation: Cardholder failed to attempt direct merchant resolution prior to chargeback. "
                    "Case is procedurally defective under Mastercard Scheme Standards."
                )

        # Rule Check 2: Visa Compelling Evidence 3.0 (Reason Code 10.4)
        visa_ce30_eligible = False
        qualifying_txns: List[HistoricalTransaction] = []
        matched_criteria = set()

        if evidence and evidence.ce30_qualifying_transactions:
            dispute_time = dispute.create_time
            current_ip = dispute.buyer_info.ip_address if dispute.buyer_info else None
            current_zip = (
                dispute.buyer_info.shipping_address.get("postal_code")
                if dispute.buyer_info and dispute.buyer_info.shipping_address
                else None
            )

            for txn in evidence.ce30_qualifying_transactions:
                if txn.was_disputed:
                    continue

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

            if len(qualifying_txns) >= 2 and len(matched_criteria) > 0:
                visa_ce30_eligible = True
                citations.append(
                    f"Visa CE 3.0 Qualified (Reason Code 10.4): Located {len(qualifying_txns)} qualifying settled transactions "
                    f"within 120-365 days matching {list(matched_criteria)}. Liability shifts to issuer automatically."
                )

        liability_shift = visa_ce30_eligible or procedural_defect

        full_citation = " | ".join(citations) if citations else "Standard representment required under scheme guidelines."

        logger.info(
            f"[ComplianceAgent] Scheme: {dispute.scheme.value}, CE 3.0: {visa_ce30_eligible}, "
            f"Procedural Defect: {procedural_defect}, Liability Shift: {liability_shift}"
        )

        return ComplianceAssessment(
            visa_ce30_eligible=visa_ce30_eligible,
            qualifying_orders_count=len(qualifying_txns),
            matched_criteria=list(matched_criteria),
            mastercard_rule_code="4853_DEFECTIVE" if procedural_defect else ("4837_DEFENDED" if visa_ce30_eligible else None),
            mastercard_prior_contact_verified=mastercard_contact_verified,
            procedural_defect_identified=procedural_defect,
            liability_shift_guaranteed=liability_shift,
            citation=full_citation
        )


compliance_agent = ComplianceAgent()

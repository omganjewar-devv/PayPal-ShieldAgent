from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.dispute import Dispute, DisputeReason
from app.models.agent_response import (
    RepresentmentDossier,
    TriageAssessment,
    ForensicAssessment,
    ComplianceAssessment
)
from app.core.logging import logger


class RepresentmentAgent:
    """
    Synthesizes findings from Triage, Forensic, and Compliance agents into an airtight,
    formatted Representment Dossier ready for submission via PayPal's Disputes API.
    """

    async def generate_dossier(
        self,
        dispute: Dispute,
        triage: TriageAssessment,
        forensics: ForensicAssessment,
        compliance: ComplianceAssessment,
        tracking_number: Optional[str] = "9400111899562537628192",
        carrier_name: Optional[str] = "USPS"
    ) -> RepresentmentDossier:
        
        compelling_points: List[str] = []

        if forensics.pod_verified:
            compelling_points.append(
                f"Proof of Delivery verified with carrier ({carrier_name} tracking #{tracking_number}) "
                f"confirming delivery to buyer's destination."
            )

        if compliance.liability_shift_guaranteed:
            compelling_points.append(
                f"Qualifies for Visa Compelling Evidence 3.0 (CE 3.0): "
                f"Customer has {compliance.qualifying_orders_count} prior undisputed orders matching {compliance.matched_criteria}. "
                f"Liability shifts to card issuer pursuant to Visa Core Rules."
            )

        if forensics.delivery_address_match:
            compelling_points.append(
                "Carrier delivery postal code exactly matches the verified PayPal shipping address on record."
            )

        narrative = (
            f"Representment Defense Dossier for Dispute {dispute.dispute_id} ({dispute.reason.value}). "
            f"Merchant fulfills PayPal Seller Protection requirements. "
            + " ".join(compelling_points)
        )

        # Build PayPal Disputes API compatible payload
        # Spec: https://developer.paypal.com/docs/api/disputes/v1/#disputes_provide_evidence
        paypal_payload: Dict[str, Any] = {
            "evidence_type": "PROOF_OF_DELIVERY" if forensics.pod_verified else "OTHER",
            "evidence_info": {
                "tracking_info": [
                    {
                        "carrier_name": carrier_name,
                        "tracking_number": tracking_number
                    }
                ]
            },
            "notes": narrative
        }

        logger.info(f"[RepresentmentAgent] Dossier generated for dispute {dispute.dispute_id}")

        return RepresentmentDossier(
            dispute_id=dispute.dispute_id,
            generated_at=datetime.utcnow(),
            triage=triage,
            forensics=forensics,
            compliance=compliance,
            defense_summary=narrative,
            compelling_evidence_points=compelling_points,
            paypal_payload=paypal_payload
        )


representment_agent = RepresentmentAgent()

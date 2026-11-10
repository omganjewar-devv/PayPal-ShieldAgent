from typing import Optional, Dict, Any
from app.models.dispute import Dispute
from app.models.evidence import EvidencePackage
from app.models.agent_response import RepresentmentDossier, DefenseAction
from app.agents.triage_agent import triage_agent
from app.agents.forensic_agent import forensic_agent
from app.agents.compliance_agent import compliance_agent
from app.agents.representment_agent import representment_agent
from app.services.paypal_client import paypal_client
from app.core.config import settings
from app.core.logging import logger


class ShieldOrchestrator:
    """
    Coordinates the multi-agent defense workflow:
    Dispute Ingestion -> Triage -> Forensic Audit -> Compliance (CE 3.0) -> Representment -> Submission
    """

    async def defend_dispute(
        self,
        dispute: Dispute,
        evidence: Optional[EvidencePackage] = None,
        force_auto_submit: bool = False
    ) -> RepresentmentDossier:
        logger.info(f"[Orchestrator] Starting dispute defense pipeline for {dispute.dispute_id}")

        # Step 1: Initial Triage
        triage = await triage_agent.evaluate(dispute)

        # Step 2: Forensic Evidence Audit
        forensics = await forensic_agent.audit(dispute, evidence)

        # Step 3: Card Network Compliance Check (Visa CE 3.0)
        compliance = await compliance_agent.verify_ce30(dispute, evidence)

        # Step 4: Dynamic Re-scoring based on empirical findings
        if compliance.liability_shift_guaranteed:
            triage.win_probability = 98.0
            triage.recommended_action = DefenseAction.DEFEND
        elif forensics.pod_verified and forensics.delivery_address_match:
            triage.win_probability = 92.0
            triage.recommended_action = DefenseAction.DEFEND
        elif forensics.evidence_tampering_flagged:
            triage.win_probability = 85.0
            triage.recommended_action = DefenseAction.DEFEND

        # Step 5: Synthesize Representment Dossier
        dossier = await representment_agent.generate_dossier(
            dispute=dispute,
            triage=triage,
            forensics=forensics,
            compliance=compliance
        )

        # Step 6: Autonomous Execution via PayPal Disputes API
        should_submit = force_auto_submit or settings.ENABLE_AUTONOMOUS_SUBMISSION

        if should_submit:
            if triage.recommended_action == DefenseAction.DEFEND:
                logger.info(f"[Orchestrator] Autonomous Action: Submitting evidence for {dispute.dispute_id}")
                await paypal_client.provide_evidence(dispute.dispute_id, dossier.paypal_payload)
            elif triage.recommended_action == DefenseAction.AUTO_CONCEDE:
                logger.info(f"[Orchestrator] Autonomous Action: Conceding claim to save fees for {dispute.dispute_id}")
                await paypal_client.accept_claim(dispute.dispute_id)

        return dossier


shield_orchestrator = ShieldOrchestrator()

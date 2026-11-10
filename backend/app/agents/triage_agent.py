from app.models.dispute import Dispute, DisputeReason
from app.models.agent_response import TriageAssessment, DefenseAction
from app.core.config import settings
from app.core.logging import logger
from datetime import datetime


class TriageAgent:
    """
    Evaluates whether a dispute is economically and tactically worth defending.
    Calculates estimated Win Probability and net Financial ROI.
    """

    async def evaluate(self, dispute: Dispute) -> TriageAssessment:
        amount = float(dispute.dispute_amount.value)
        dispute_fee = 20.0  # Typical card network chargeback fee ($15 - $25)

        risk_factors = []
        base_win_prob = 50.0

        # Factor 1: Reason Code heuristics
        if dispute.reason == DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED:
            # INR is the easiest to defend with valid carrier tracking / POD
            base_win_prob = 75.0
        elif dispute.reason == DisputeReason.UNAUTHORISED:
            # Fraud claims depend heavily on CE 3.0 or 3DS
            base_win_prob = 65.0
        elif dispute.reason == DisputeReason.MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED:
            # Subjective dispute, slightly harder
            base_win_prob = 40.0
            risk_factors.append("Subjective SNAD claim typically favors the buyer without strict return policy proof")

        # Factor 2: Financial Viability & Micro-chargeback triage
        # If dispute amount is $10, and defending risks a $20 fee + hours of review,
        # it is often smarter to concede early unless win prob is near-certain.
        expected_win_value = (base_win_prob / 100.0) * amount
        expected_loss_cost = ((100.0 - base_win_prob) / 100.0) * (amount + dispute_fee)
        net_roi = expected_win_value - expected_loss_cost

        # Factor 3: Time urgency
        hours_remaining = None
        if dispute.seller_response_due_date:
            delta = dispute.seller_response_due_date - datetime.utcnow()
            hours_remaining = max(0.0, delta.total_seconds() / 3600.0)
            if hours_remaining < 24.0:
                risk_factors.append(f"Urgent SLA: only {hours_remaining:.1f} hours remaining before default loss")

        # Decision Logic
        if amount <= settings.MAX_DISPUTE_AMOUNT_FOR_AUTO_CONCEDE and base_win_prob < 50.0:
            recommended_action = DefenseAction.AUTO_CONCEDE
            risk_factors.append("Dispute value is below economic defense threshold with low win confidence")
        elif base_win_prob >= settings.MIN_WIN_PROBABILITY_TO_DEFEND:
            recommended_action = DefenseAction.DEFEND
        else:
            recommended_action = DefenseAction.MANUAL_REVIEW

        assessment = TriageAssessment(
            dispute_id=dispute.dispute_id,
            win_probability=base_win_prob,
            financial_roi=round(net_roi, 2),
            urgency_hours_remaining=hours_remaining,
            recommended_action=recommended_action,
            risk_factors=risk_factors,
            confidence_score=0.85
        )

        logger.info(f"[TriageAgent] Dispute {dispute.dispute_id} -> Action: {recommended_action}, Win Prob: {base_win_prob}%")
        return assessment


triage_agent = TriageAgent()

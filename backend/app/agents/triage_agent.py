from app.models.dispute import Dispute, DisputeReason, DisputeLifeCycleStage
from app.models.agent_response import TriageAssessment, DefenseAction, ArbitrationRiskAssessment
from app.core.config import settings
from app.core.logging import logger
from datetime import datetime


class TriageAgent:
    """
    Evaluates whether a dispute is economically and tactically worth defending.
    Includes:
    - Staggered Scheme SLA / Deadline Engine (detects Day N-1 critical windows).
    - Arbitration Go/No-Go Decision Engine (evaluates $500 scheme filing fee risk).
    """

    async def evaluate(self, dispute: Dispute) -> TriageAssessment:
        amount = float(dispute.dispute_amount.value)
        dispute_fee = 20.0  # Typical card network chargeback fee ($15 - $25)

        risk_factors = []
        base_win_prob = 50.0

        # Factor 1: Reason Code heuristics
        if dispute.reason == DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED:
            base_win_prob = 75.0
        elif dispute.reason == DisputeReason.UNAUTHORISED:
            base_win_prob = 65.0
        elif dispute.reason == DisputeReason.MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED:
            base_win_prob = 40.0
            risk_factors.append("Subjective SNAD claim: Scheme burden of proof favors cardholder without return policy evidence.")

        # Factor 2: Staggered Deadline & SLA Calculation (Day N-1 boundary checks)
        hours_remaining = None
        sla_urgency_tier = "NORMAL"

        deadline = dispute.seller_response_due_date or dispute.scheme_deadline
        if deadline:
            delta = deadline - datetime.utcnow()
            hours_remaining = delta.total_seconds() / 3600.0

            if hours_remaining <= 0:
                sla_urgency_tier = "EXPIRED"
                risk_factors.append("SLA EXPIRED: Past scheme deadline window. Default loss risk.")
            elif hours_remaining <= 24.0:
                sla_urgency_tier = "CRITICAL_DAY_N_MINUS_1"
                risk_factors.append(f"Day N-1 Critical Alert: Only {hours_remaining:.1f} hours left before default loss.")
            elif hours_remaining <= 72.0:
                sla_urgency_tier = "URGENT"
                risk_factors.append(f"Urgent SLA window: {hours_remaining:.1f} hours remaining.")

        # Factor 3: Scheme Arbitration Go/No-Go Decision (Stages 7 & 9)
        arbitration_risk = None
        is_arbitration = dispute.dispute_life_cycle_stage in [
            DisputeLifeCycleStage.PRE_ARBITRATION,
            DisputeLifeCycleStage.SCHEME_ARBITRATION
        ]

        if is_arbitration:
            scheme_fee = 500.0  # Visa/Mastercard formal arbitration filing fee for losing party
            win_rate_dec = base_win_prob / 100.0
            loss_rate_dec = 1.0 - win_rate_dec

            # EV = (WinRate * Amount) - (LossRate * (Amount + SchemeFee))
            expected_arbitration_val = (win_rate_dec * amount) - (loss_rate_dec * (amount + scheme_fee))

            # Only proceed to arbitration if expected value is positive and win rate >= 85%
            go_decision = expected_arbitration_val > 0 and base_win_prob >= 85.0

            rationale = (
                f"Arbitration EV is ${expected_arbitration_val:.2f}. "
                + ("Proceed: Evidence is compelling and justifies risking $500 filing fee."
                   if go_decision
                   else "Concede: Risk of $500 scheme filing fee outweighs disputed amount.")
            )

            arbitration_risk = ArbitrationRiskAssessment(
                is_arbitration_stage=True,
                scheme_filing_fee=scheme_fee,
                win_probability=base_win_prob,
                dispute_amount=amount,
                expected_value_if_escalated=round(expected_arbitration_val, 2),
                go_decision=go_decision,
                rationale=rationale
            )

            if not go_decision:
                recommended_action = DefenseAction.CONCEDE_ARBITRATION
                risk_factors.append("High Scheme Arbitration fee ($500) makes defense mathematically negative EV.")
            else:
                recommended_action = DefenseAction.DEFEND

            net_roi = expected_arbitration_val
        else:
            # Standard Stage 4/5 Representment Triage
            expected_win_value = (base_win_prob / 100.0) * amount
            expected_loss_cost = ((100.0 - base_win_prob) / 100.0) * (amount + dispute_fee)
            net_roi = expected_win_value - expected_loss_cost

            if amount <= settings.MAX_DISPUTE_AMOUNT_FOR_AUTO_CONCEDE and base_win_prob < 50.0:
                recommended_action = DefenseAction.AUTO_CONCEDE
                risk_factors.append("Dispute value below economic defense threshold; auto-concede to save $20 network fee.")
            elif base_win_prob >= settings.MIN_WIN_PROBABILITY_TO_DEFEND:
                recommended_action = DefenseAction.DEFEND
            else:
                recommended_action = DefenseAction.MANUAL_REVIEW

        assessment = TriageAssessment(
            dispute_id=dispute.dispute_id,
            current_stage=dispute.dispute_life_cycle_stage,
            win_probability=base_win_prob,
            financial_roi=round(net_roi, 2),
            urgency_hours_remaining=hours_remaining,
            sla_urgency_tier=sla_urgency_tier,
            recommended_action=recommended_action,
            risk_factors=risk_factors,
            confidence_score=0.88,
            arbitration_risk=arbitration_risk
        )

        logger.info(
            f"[TriageAgent] Dispute {dispute.dispute_id} (Stage: {dispute.dispute_life_cycle_stage.value}) -> "
            f"Action: {recommended_action.value}, SLA: {sla_urgency_tier}"
        )
        return assessment


triage_agent = TriageAgent()

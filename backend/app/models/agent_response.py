from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.dispute import DisputeLifeCycleStage


class DefenseAction(str, Enum):
    DEFEND = "DEFEND"
    AUTO_CONCEDE = "AUTO_CONCEDE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    CONCEDE_ARBITRATION = "CONCEDE_ARBITRATION"  # Concede at Stage 7/9 to avoid $500 network fee


class ArbitrationRiskAssessment(BaseModel):
    is_arbitration_stage: bool = False
    scheme_filing_fee: float = 500.0  # Visa/Mastercard standard scheme filing fee
    win_probability: float
    dispute_amount: float
    expected_value_if_escalated: float
    go_decision: bool  # True = proceed to scheme arbitration, False = concede early to save $500 fee
    rationale: str


class TriageAssessment(BaseModel):
    dispute_id: str
    current_stage: DisputeLifeCycleStage = DisputeLifeCycleStage.FIRST_CHARGEBACK
    win_probability: float = Field(..., ge=0.0, le=100.0, description="Estimated win chance percentage")
    financial_roi: float = Field(..., description="Estimated net expected value of defending")
    urgency_hours_remaining: Optional[float] = None
    sla_urgency_tier: str = "NORMAL"  # CRITICAL_DAY_N_MINUS_1, URGENT, NORMAL, EXPIRED
    recommended_action: DefenseAction
    risk_factors: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0
    arbitration_risk: Optional[ArbitrationRiskAssessment] = None


class ForensicAssessment(BaseModel):
    pod_verified: bool = False
    delivery_address_match: bool = False
    exif_valid: bool = False
    evidence_tampering_flagged: bool = False
    damage_claim_plausibility: Optional[str] = None
    fraud_indicators: List[str] = Field(default_factory=list)
    summary: str


class ComplianceAssessment(BaseModel):
    visa_ce30_eligible: bool = False
    qualifying_orders_count: int = 0
    matched_criteria: List[str] = Field(default_factory=list)  # e.g., ["IP_ADDRESS", "SHIPPING_ADDRESS"]
    mastercard_rule_code: Optional[str] = None
    mastercard_prior_contact_verified: bool = True
    procedural_defect_identified: bool = False
    liability_shift_guaranteed: bool = False
    citation: Optional[str] = None


class RepresentmentDossier(BaseModel):
    dispute_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    triage: TriageAssessment
    forensics: ForensicAssessment
    compliance: ComplianceAssessment
    defense_summary: str
    compelling_evidence_points: List[str]
    paypal_payload: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Formatted payload ready to POST to PayPal /provide-evidence endpoint"
    )

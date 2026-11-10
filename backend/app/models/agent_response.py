from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DefenseAction(str, Enum):
    DEFEND = "DEFEND"
    AUTO_CONCEDE = "AUTO_CONCEDE"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class TriageAssessment(BaseModel):
    dispute_id: str
    win_probability: float = Field(..., ge=0.0, le=100.0, description="Estimated win chance percentage")
    financial_roi: float = Field(..., description="Estimated net expected value of defending")
    urgency_hours_remaining: Optional[float] = None
    recommended_action: DefenseAction
    risk_factors: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0


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
    matched_criteria: List[str] = Field(default_factory=list)  # e.g., ["IP_ADDRESS", "DEVICE_FINGERPRINT"]
    mastercard_rule_code: Optional[str] = None
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

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CardScheme(str, Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMEX = "AMEX"
    PAYPAL_BALANCE = "PAYPAL_BALANCE"


class DisputeReason(str, Enum):
    MERCHANDISE_OR_SERVICE_NOT_RECEIVED = "MERCHANDISE_OR_SERVICE_NOT_RECEIVED"  # INR
    MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED = "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED"  # SNAD
    UNAUTHORISED = "UNAUTHORISED"  # Friendly Fraud / Card Fraud
    CANCELED_RECURRING_BILLING = "CANCELED_RECURRING_BILLING"
    CREDIT_NOT_PROCESSED = "CREDIT_NOT_PROCESSED"
    DUPLICATE_TRANSACTION = "DUPLICATE_TRANSACTION"
    INCORRECT_AMOUNT = "INCORRECT_AMOUNT"
    OTHER = "OTHER"


class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    WAITING_FOR_BUYER_RESPONSE = "WAITING_FOR_BUYER_RESPONSE"
    WAITING_FOR_SELLER_RESPONSE = "WAITING_FOR_SELLER_RESPONSE"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class DisputeLifeCycleStage(str, Enum):
    """
    Full 10-Stage Issuer/Acquirer Scheme Lifecycle:
    Intake -> Triage -> First Chargeback -> Representment -> Issuer Review -> Pre-Arbitration -> Scheme Arbitration -> Closure
    """
    INQUIRY = "INQUIRY"                                  # Stage 1: Internal PayPal resolution
    TRIAGE = "TRIAGE"                                    # Stage 2: Eligibility & reason code selection
    FIRST_CHARGEBACK = "FIRST_CHARGEBACK"                # Stage 4: Network chargeback raised via VROL / Mastercom
    MERCHANT_REPRESENTMENT = "MERCHANT_REPRESENTMENT"    # Stage 5: Merchant defends with evidence dossier
    ISSUER_REVIEW = "ISSUER_REVIEW"                      # Stage 6: Issuer (e.g. Barclays) reviews representment under scheme rules
    PRE_ARBITRATION = "PRE_ARBITRATION"                  # Stage 7: Escalation before formal scheme filing
    SCHEME_ARBITRATION = "SCHEME_ARBITRATION"            # Stage 9: Visa/Mastercard scheme ruling ($500+ fee for loser)
    CLOSURE = "CLOSURE"                                  # Stage 10: Financial settlement & case resolved


class Money(BaseModel):
    currency_code: str = "USD"
    value: str = "0.00"


class BuyerInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    payer_id: Optional[str] = None
    ip_address: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None


class DisputedTransaction(BaseModel):
    transaction_id: str
    order_id: Optional[str] = None
    gross_amount: Money
    create_time: datetime
    custom_id: Optional[str] = None
    invoice_number: Optional[str] = None


class Dispute(BaseModel):
    dispute_id: str
    create_time: datetime
    update_time: Optional[datetime] = None
    disputed_transactions: List[DisputedTransaction]
    reason: DisputeReason
    status: DisputeStatus
    dispute_amount: Money
    dispute_life_cycle_stage: DisputeLifeCycleStage
    
    # Scheme & Issuer Attributes (e.g., Barclays / Visa / Mastercard)
    scheme: CardScheme = CardScheme.VISA
    scheme_reason_code: Optional[str] = None  # e.g., "10.4" (Visa Fraud) or "4837" (Mastercard Fraud)
    buyer_contacted_merchant: Optional[bool] = None  # Mandatory check under Mastercard dispute rules
    
    buyer_info: Optional[BuyerInfo] = None
    seller_response_due_date: Optional[datetime] = None
    scheme_deadline: Optional[datetime] = None  # Staggered scheme network window
    raw_payload: Optional[Dict[str, Any]] = None

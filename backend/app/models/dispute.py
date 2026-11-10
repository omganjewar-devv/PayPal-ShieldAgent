from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


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
    INQUIRY = "INQUIRY"
    CHARGEBACK = "CHARGEBACK"
    PRE_ARBITRATION = "PRE_ARBITRATION"
    ARBITRATION = "ARBITRATION"


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
    buyer_info: Optional[BuyerInfo] = None
    seller_response_due_date: Optional[datetime] = None
    raw_payload: Optional[Dict[str, Any]] = None

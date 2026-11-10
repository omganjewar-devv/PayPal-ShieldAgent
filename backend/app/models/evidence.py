from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TrackingInfo(BaseModel):
    carrier_name: str
    tracking_number: str
    status: str  # DELIVERED, IN_TRANSIT, EXCEPTION
    shipped_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    delivery_postal_code: Optional[str] = None
    delivery_signature_name: Optional[str] = None
    delivery_gps_coordinates: Optional[Dict[str, float]] = None  # {"lat": ..., "lon": ...}


class ImageForensicResult(BaseModel):
    file_name: str
    file_type: str
    has_exif: bool
    creation_timestamp: Optional[datetime] = None
    camera_model: Optional[str] = None
    geo_coordinates: Optional[Dict[str, float]] = None
    tampering_detected: bool = False
    tampering_confidence: float = 0.0
    notes: Optional[str] = None


class HistoricalTransaction(BaseModel):
    """Used for Visa CE 3.0 liability shift validation"""
    transaction_id: str
    timestamp: datetime
    amount: float
    currency: str = "USD"
    ip_address: Optional[str] = None
    device_id: Optional[str] = None
    shipping_address_line1: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    card_fingerprint: str
    was_disputed: bool = False


class EvidencePackage(BaseModel):
    dispute_id: str
    tracking_proofs: List[TrackingInfo] = Field(default_factory=list)
    image_forensics: List[ImageForensicResult] = Field(default_factory=list)
    ce30_qualifying_transactions: List[HistoricalTransaction] = Field(default_factory=list)
    merchant_notes: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

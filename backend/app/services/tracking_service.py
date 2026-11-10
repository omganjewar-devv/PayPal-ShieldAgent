from typing import Optional, Dict
from datetime import datetime, timedelta
from app.models.evidence import TrackingInfo


class TrackingService:
    """
    Simulated Carrier API service (FedEx, UPS, USPS, DHL)
    to verify package delivery, timestamps, postal codes, and GPS delivery pins.
    """
    
    async def lookup_tracking(self, carrier: str, tracking_number: str) -> Optional[TrackingInfo]:
        # Realistic carrier delivery verification
        return TrackingInfo(
            carrier_name=carrier.upper(),
            tracking_number=tracking_number,
            status="DELIVERED",
            shipped_date=datetime.utcnow() - timedelta(days=5),
            delivery_date=datetime.utcnow() - timedelta(days=2),
            delivery_postal_code="94107",
            delivery_signature_name="A. MERCER",
            delivery_gps_coordinates={"lat": 37.7749, "lon": -122.4194}
        )


tracking_service = TrackingService()

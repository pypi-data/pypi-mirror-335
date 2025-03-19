from pydantic import BaseModel

class TrackingNumberInfo(BaseModel):
    trackingNumber: str
    trackingNumberUniqueId: str
    carrierCode: str
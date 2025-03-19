from pydantic import BaseModel

class TrackingId(BaseModel):
    trackingIdType: str
    formId: str
    trackingNumber: str
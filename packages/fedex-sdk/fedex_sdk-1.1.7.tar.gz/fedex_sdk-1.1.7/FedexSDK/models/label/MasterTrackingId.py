from pydantic import BaseModel

class MasterTrackingId(BaseModel):
    trackingIdType: str
    formId: str
    trackingNumber: str
    
    

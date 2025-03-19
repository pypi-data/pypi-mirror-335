from pydantic import BaseModel

class AdditionalTrackingInfo(BaseModel):
    nickname: str
    hasAssociatedShipments: bool
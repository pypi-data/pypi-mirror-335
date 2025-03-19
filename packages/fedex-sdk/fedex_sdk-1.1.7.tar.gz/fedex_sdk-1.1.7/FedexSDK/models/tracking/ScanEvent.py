from pydantic import BaseModel
from typing import Optional

from .DelayDetail import DelayDetail

from .ScanLocation import ScanLocation

class ScanEvent(BaseModel):
    date: str
    eventType: str
    eventDescription: str
    exceptionCode: str
    exceptionDescription: str
    scanLocation: ScanLocation
    locationId: Optional[str] = None
    locationType: str
    derivedStatusCode: str
    derivedStatus: str
    delayDetail: Optional[DelayDetail] = None
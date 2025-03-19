from pydantic import BaseModel
from .DelayDetail import DelayDetail
from .ScanLocation import ScanLocation
from typing import Optional

class LatestStatusDetail(BaseModel):
    code: str
    derivedCode: str
    statusByLocale: str
    description: str
    scanLocation: ScanLocation
    delayDetail: Optional[DelayDetail]
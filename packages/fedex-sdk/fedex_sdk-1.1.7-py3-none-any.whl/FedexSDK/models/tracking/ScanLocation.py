from pydantic import BaseModel
from typing import List, Optional

class ScanLocation(BaseModel):
    streetLines: Optional[List[str]]
    city: Optional[str] = None
    stateOrProvinceCode: Optional[str] = None
    postalCode: Optional[str] = None
    countryCode: Optional[str] = None
    residential: bool
    countryName: Optional[str] = None
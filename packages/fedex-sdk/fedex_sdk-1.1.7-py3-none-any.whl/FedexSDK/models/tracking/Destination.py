from pydantic import BaseModel
from typing import Optional

from .LocationContactAndAddress import LocationContactAndAddress

class DestinationLocation(BaseModel):
    locationContactAndAddress: LocationContactAndAddress
    locationType: str


class LastUpdatedDestinationAddress(BaseModel):
    city: str
    stateOrProvinceCode: Optional[str]
    countryCode: str
    residential: bool
    countryName: str
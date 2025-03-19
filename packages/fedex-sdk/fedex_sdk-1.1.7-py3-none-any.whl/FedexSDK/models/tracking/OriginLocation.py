from pydantic import BaseModel
from .LocationContactAndAddress import LocationContactAndAddress
from typing import Optional

class OriginLocation(BaseModel):
    locationContactAndAddress: LocationContactAndAddress
    locationId: Optional[str]
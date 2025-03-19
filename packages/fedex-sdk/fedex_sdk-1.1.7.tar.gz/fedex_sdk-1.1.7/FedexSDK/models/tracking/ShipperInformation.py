from typing import Dict, Any, Optional
from .Address import Address
from pydantic import BaseModel

class ShipperInformation(BaseModel):
    contact: Optional[Dict[str, Any]] = None
    address: Address
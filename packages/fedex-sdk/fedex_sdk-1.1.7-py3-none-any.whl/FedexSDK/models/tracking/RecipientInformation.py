from typing import Dict, Any, Optional
from pydantic import BaseModel
from .Address import Address

class RecipientInformation(BaseModel):
    contact: Optional[Dict[str, Any]]
    address: Address
from typing import List, Optional
from pydantic import BaseModel

from .Address import Address
from .Contact import Contact
from .Tin import Tin

class Recipient(BaseModel):
    address: Address
    contact: Contact
    tins: Optional[List[Tin]]
    deliveryInstructions: str = ""
    
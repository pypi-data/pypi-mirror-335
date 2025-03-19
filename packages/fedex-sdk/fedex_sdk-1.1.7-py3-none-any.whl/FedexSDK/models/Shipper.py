from typing import List, Optional
from pydantic import BaseModel

from .Tin import Tin

from .Address import Address
from .Contact import Contact


class Shipper(BaseModel):
    address: Address
    contact: Contact
    tins: Optional[List[Tin]]
    
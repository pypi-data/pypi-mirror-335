from typing import List
from pydantic import BaseModel

from .AccountNumber import AccountNumber

from .Address import Address
from .Contact import Contact
from .Tin import Tin

class SoldTo(BaseModel):
    address: Address
    contact: Contact
    tins: List[Tin]
    accountNumber: AccountNumber
    
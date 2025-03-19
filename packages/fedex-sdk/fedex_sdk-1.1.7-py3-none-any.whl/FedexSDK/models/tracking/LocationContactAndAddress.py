from pydantic import BaseModel
from .Address import Address


class LocationContactAndAddress(BaseModel):
    address: Address
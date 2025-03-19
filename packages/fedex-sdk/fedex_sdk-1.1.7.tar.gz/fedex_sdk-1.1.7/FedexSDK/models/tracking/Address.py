from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    city: str
    stateOrProvinceCode: Optional[str]
    countryCode: str
    residential: bool
    countryName: str
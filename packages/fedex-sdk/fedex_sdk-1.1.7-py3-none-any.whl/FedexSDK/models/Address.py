from typing import List
from pydantic import BaseModel, validator


class Address(BaseModel):
    streetLines: List[str]
    city: str
    countryCode: str
    
    stateOrProvinceCode: str = ""
    postalCode: str = ""
    residential: bool = True
    
    @validator("streetLines", allow_reuse=True)
    def street_lines_validate(cls, value: List[str]):
        for line in value:
            if len(line) > 35:
                raise ValueError(
                    "Street Line Max Length 35!"
                )
            else:
                if len(line) == 0:
                    value.remove(line)
        return value
    
    @validator("city", allow_reuse=True)
    def city_validate(cls, value: str):
        if len(value) > 35:
            raise ValueError(
                "City Max Length 35!"
            )
        return value
    
    @validator("postalCode", allow_reuse=True)
    def postal_code_validate(cls, value: str):
        if len(value) > 10:
            raise ValueError(
                "Postal Code Max Length 10!"
            )
            
        return value
    
    @validator("countryCode", allow_reuse=True)
    def country_code_validate(cls, value: str):
        if len(value) > 2:
            raise ValueError(
                "Country Code Max Length 2!"
            )
        return value
            
    
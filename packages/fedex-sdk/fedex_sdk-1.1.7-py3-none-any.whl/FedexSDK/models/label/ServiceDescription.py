from typing import List
from pydantic import BaseModel
from .Name import Name

class ServiceDescription(BaseModel):
    serviceId: str
    serviceType: str
    code: str
    names: List[Name]
    operatingOrgCodes: List[str]
    serviceCategory: str
    description: str
    astraDescription: str
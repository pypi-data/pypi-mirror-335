from typing import List

from .WeightAndDimensions import WeightAndDimensions
from pydantic import BaseModel

class PackagingDescription(BaseModel):
    type: str
    description: str

class PackageDetails(BaseModel):
    packagingDescription: PackagingDescription
    sequenceNumber: str
    count: str
    weightAndDimensions: WeightAndDimensions
    packageContent: List
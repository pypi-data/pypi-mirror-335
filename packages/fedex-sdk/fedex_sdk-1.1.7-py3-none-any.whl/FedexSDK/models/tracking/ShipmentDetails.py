from typing import List
from pydantic import BaseModel

from .WeightAndDimensions import WeightItem


class ShipmentDetails(BaseModel):
    possessionStatus: bool
    weight: List[WeightItem]
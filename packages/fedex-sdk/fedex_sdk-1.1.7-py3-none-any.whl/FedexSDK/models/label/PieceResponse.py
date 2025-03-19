from pydantic import BaseModel
from typing import List

from .PackageDocument import PackageDocument

class PieceResponse(BaseModel):
    masterTrackingNumber: str
    trackingNumber: str
    additionalChargesDiscount: float
    netRateAmount: float
    netChargeAmount: float
    netDiscountAmount: float
    packageDocuments: List[PackageDocument]
    customerReferences: List
    codcollectionAmount: float
    baseRateAmount: float
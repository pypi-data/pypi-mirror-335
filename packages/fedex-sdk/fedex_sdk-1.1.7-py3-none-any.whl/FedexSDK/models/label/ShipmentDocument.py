from typing import List, Optional
from pydantic import BaseModel

from .Part import Part

class ShipmentDocument(BaseModel):
    type: Optional[str]
    shippingDocumentDisposition: Optional[str]
    imageType: Optional[str]
    resolution: Optional[int]
    copiesToPrint: Optional[int]
    parts: Optional[List[Part]]
    contentKey: Optional[str]
    contentType: Optional[str]
    copiesToPrint: Optional[int]
    encodedLabel: Optional[str]
    trackingNumber: Optional[str]
    docType: Optional[str]
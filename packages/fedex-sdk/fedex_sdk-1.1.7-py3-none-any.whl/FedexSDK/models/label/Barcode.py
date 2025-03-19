from typing import List
from pydantic import BaseModel


class BinaryBarcode(BaseModel):
    type: str
    value: str
    
class StringBarcode(BaseModel):
    type: str
    value: str
    
class Barcodes(BaseModel):
    binaryBarcodes: List[BinaryBarcode]
    stringBarcodes: List[StringBarcode]
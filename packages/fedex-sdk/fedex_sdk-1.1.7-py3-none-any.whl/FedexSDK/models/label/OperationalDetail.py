from typing import List
from pydantic import BaseModel

from .OperationalInsturaction import OperationalInstruction

from .Barcode import Barcodes

class OperationalDetail(BaseModel):
    ursaPrefixCode: str
    ursaSuffixCode: str
    originLocationId: str
    originLocationNumber: int
    originServiceArea: str
    destinationLocationId: str
    destinationLocationNumber: int
    destinationServiceArea: str
    destinationLocationStateOrProvinceCode: str
    deliveryDate: str
    deliveryDay: str
    commitDate: str
    commitDay: str
    ineligibleForMoneyBackGuarantee: bool
    astraPlannedServiceLevel: str
    astraDescription: str
    postalCode: str
    stateOrProvinceCode: str
    countryCode: str
    airportId: str
    serviceCode: str
    packagingCode: str
    publishedDeliveryTime: str
    scac: str
    

class CompletedPackageDetailOperationalDetail(BaseModel):
    barcodes: Barcodes
    astraHandlingText: str
    operationalInstructions: List[OperationalInstruction]
    
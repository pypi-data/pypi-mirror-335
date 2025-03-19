from pydantic import BaseModel
from typing import List

from .MasterTrackingId import MasterTrackingId

from .ServiceDescription import ServiceDescription

from .CompletedEtdDetail import CompletedEtdDetail

from .DocumentRequirements import DocumentRequirements

from .CompletedPackageDetail import CompletedPackageDetail

from .ShipmentDocument import ShipmentDocument

from .OperationalDetail import OperationalDetail


class CompletedShipmentDetail(BaseModel):
    usDomestic: bool
    carrierCode: str
    masterTrackingId: MasterTrackingId
    serviceDescription: ServiceDescription
    packagingDescription: str
    operationalDetail: OperationalDetail
    completedPackageDetails: List[CompletedPackageDetail]
    documentRequirements: DocumentRequirements
    completedEtdDetail: CompletedEtdDetail
    shipmentDocuments: List[ShipmentDocument]
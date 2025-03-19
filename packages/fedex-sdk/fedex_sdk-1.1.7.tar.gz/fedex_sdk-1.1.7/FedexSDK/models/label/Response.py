from pydantic import BaseModel
from typing import List, Dict, Any
from .ShipmentDocument import ShipmentDocument
from .PieceResponse import PieceResponse
from .CompletedShipmentDetail import CompletedShipmentDetail

class TransactionShipment(BaseModel):
    masterTrackingNumber: str
    serviceType: str
    shipDatestamp: str
    serviceName: str
    shipmentDocuments: List[ShipmentDocument]
    pieceResponses: List[PieceResponse]
    shipmentAdvisoryDetails: Dict[str, Any]
    completedShipmentDetail: CompletedShipmentDetail
    serviceCategory: str


class Output(BaseModel):
    transactionShipments: List[TransactionShipment]


class LabelResponse(BaseModel):
    transactionId: str
    output: Output

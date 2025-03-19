from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .ServiceCommitMessage import ServiceCommitMessage
from .Destination import DestinationLocation, LastUpdatedDestinationAddress
from .OriginLocation import OriginLocation
from .DeliveryDetails import DeliveryDetails
from .SpecialHandling import SpecialHandling
from .DateAndTime import DateAndTime
from .LatestStatusDetail import LatestStatusDetail
from .RecipientInformation import RecipientInformation
from .ShipperInformation import ShipperInformation
from .AdditionalTrackingInfo import AdditionalTrackingInfo
from .TrackingNumberInfo import TrackingNumberInfo
from .Window import EstimatedDeliveryTimeWindow, StandardTransitTimeWindow
from .ServiceDetail import ServiceDetail
from .ScanEvent import ScanEvent
from .PackageDetails import PackageDetails
from .ShipmentDetails import ShipmentDetails

class TrackResult(BaseModel):
    trackingNumberInfo: TrackingNumberInfo
    additionalTrackingInfo: Optional[AdditionalTrackingInfo] = None
    shipperInformation: Optional[ShipperInformation] = None
    recipientInformation: Optional[RecipientInformation] = None
    latestStatusDetail: Optional[LatestStatusDetail] = None
    dateAndTimes: Optional[List[DateAndTime]] = None
    availableImages: Optional[List] = None
    specialHandlings: Optional[List[SpecialHandling]] = None
    packageDetails: Optional[PackageDetails] = None
    shipmentDetails: Optional[ShipmentDetails] = None
    scanEvents: Optional[List[ScanEvent]] = None
    availableNotifications: Optional[List[str]] = None
    deliveryDetails: Optional[DeliveryDetails] = None
    originLocation: Optional[OriginLocation] = None
    destinationLocation: Optional[DestinationLocation] = None
    lastUpdatedDestinationAddress: Optional[LastUpdatedDestinationAddress] = None
    serviceCommitMessage: Optional[ServiceCommitMessage] = None
    serviceDetail: Optional[ServiceDetail] = None
    standardTransitTimeWindow: Optional[StandardTransitTimeWindow] = None
    estimatedDeliveryTimeWindow: Optional[EstimatedDeliveryTimeWindow] = None
    goodsClassificationCode: Optional[str] = None
    returnDetail: Optional[Dict[str, Any]]

class CompleteTrackResult(BaseModel):
    trackingNumber: str
    trackResults: List[TrackResult]

class Output(BaseModel):
    completeTrackResults: List[CompleteTrackResult]
    
class TrackResponse(BaseModel):
    transactionId: str
    output: Optional[Output] = None
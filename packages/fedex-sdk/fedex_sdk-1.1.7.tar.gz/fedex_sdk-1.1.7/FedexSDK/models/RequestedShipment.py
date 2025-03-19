from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

from .AccountNumber import AccountNumber

from .Contact import Contact

from .Address import Address

from .Recipient import Recipient

from .SoldTo import SoldTo

from .Shipper import Shipper

from .TotalDeclaredValue import TotalDeclaredValue



class PickUpType(str, Enum):
    Contact_Fedex_To_Schedule: str = "CONTACT_FEDEX_TO_SCHEDULE"
    Dropoff_At_Fedex_Location: str = "DROPOFF_AT_FEDEX_LOCATION"
    Use_Schduled_Pickup: str = "USE_SCHEDULED_PICKUP"
    

class PackagingType(str, Enum):
    Your_Packaging: str = "YOUR_PACKAGING"
    Envelope: str = "FEDEX_ENVELOPE"
    Box: str = "FEDEX_BOX"
    Small_Box: str = "FEDEX_SMALL_BOX"
    Medium_Box: str = "FEDEX_MEDIUM_BOX"
    Large_Box: str = "FEDEX_LARGE_BOX"
    Extra_Large_Box: str = "FEDEX_EXTRA_LARGE_BOX"
    Ten_KG_Box: str = "FEDEX_10KG_BOX"
    Twenty_Five_KG_Box: str = "FEDEX_25KG_BOX"
    PAK: str = "FEDEX_PAK"
    TUBE: str = "FEDEX_TUBE"


class Origin(BaseModel):
    address: Address
    contact: Contact


class PaymentType(str, Enum):
    Sender: str = "SENDER"
    Recipient: str = "RECIPIENT"
    Third_Party: str = "THIRD_PARTY"
    Collect: str = "COLLECT"
    


class ResponsibleParty(BaseModel):
    address: Optional[Address]
    contact: Optional[Contact]
    accountNumber: AccountNumber


class Payor(BaseModel):
    responsibleParty: ResponsibleParty
    
    
class ShippingChargesPayment(BaseModel):
    paymentType: PaymentType = PaymentType.Sender
    payor: Optional[Payor]
    
    class Config:
        use_enum_values = True
        validate_all = True

class Unit(str, Enum):
    Cm: str = "CM"
    Inch: str = "IN"
    
class Dimensions(BaseModel):
    length: int
    width: int
    height: int
    units: Unit = Unit.Cm
    
class Weight(BaseModel):
    units: str
    value: str
    
    
class RequestedPackageLineItem(BaseModel):
    _Comment_: str
    groupPackageCount: Optional[int]
    dimensions: Optional[Dimensions]
    weight: Weight


class LabelImageType(str, Enum):
    ZPLII: str = "ZPLII"
    EPL2: str = "EPL2"
    PDF: str = "PDF"
    PNG: str = "PNG"



class LabelPrintingOrientation(str, Enum):
    BOTTOM_EDGE_OF_TEXT_FIRST: str = "BOTTOM_EDGE_OF_TEXT_FIRST"
    TOP_EDGE_OF_TEXT_FIRST: str = "TOP_EDGE_OF_TEXT_FIRST"


class LabelRotation(str, Enum):
    LEFT: str = "LEFT"
    RIGHT: str = "RIGHT"
    UPSIDE_DOWN: str = "UPSIDE_DOWN"
    NONE: str = "NONE"


class LabelStockType(str, Enum):
    PAPER_4X6: str = "PAPER_4X6"
    PAPER_4X675: str = "PAPER_4X675"
    PAPER_4X8: str = "PAPER_4X8"
    PAPER_4X9: str = "PAPER_4X9"
    PAPER_7X475: str = "PAPER_7X475"
    PAPER_85X11_BOTTOM_HALF_LABEL: str = "PAPER_85X11_BOTTOM_HALF_LABEL"
    PAPER_85X11_TOP_HALF_LABEL: str = "PAPER_85X11_TOP_HALF_LABEL"
    PAPER_LETTER: str = "PAPER_LETTER"
    STOCK_4X675_LEADING_DOC_TAB: str = "STOCK_4X675_LEADING_DOC_TAB"
    STOCK_4X8: str = "STOCK_4X8"
    STOCK_4X9_LEADING_DOC_TAB: str = "STOCK_4X9_LEADING_DOC_TAB"
    STOCK_4X6: str = "STOCK_4X6"
    STOCK_4X675_TRAILING_DOC_TAB: str = "STOCK_4X675_TRAILING_DOC_TAB"
    STOCK_4X9_TRAILING_DOC_TAB: str = "STOCK_4X9_TRAILING_DOC_TAB"
    STOCK_4X9: str = "STOCK_4X9"
    STOCK_4X85_TRAILING_DOC_TAB: str = "STOCK_4X85_TRAILING_DOC_TAB"
    STOCK_4X105_TRAILING_DOC_TAB: str = "STOCK_4X105_TRAILING_DOC_TAB"

class LabelSpecification(BaseModel):
    imageType: LabelImageType = LabelImageType.ZPLII
    labelStockType: LabelStockType = LabelStockType.PAPER_4X6
    labelPrintingOrientation: Optional[LabelPrintingOrientation]
    returnedDispositionDetail: Optional[bool]
    labelRotation: Optional[LabelRotation]
    
    class Config:
        use_enum_values = True
        validate_all = True
        


class DutiesPayment(BaseModel):
    paymentType: str


class CommercialInvoice(BaseModel):
    termsOfSale: str
    
class TotalCustomsValue(BaseModel):
    amount: str
    currency: str
    
class UnitPrice(BaseModel):
    amount: str
    currency: str


class CustomsValue(BaseModel):
    amount: str
    currency: str

class Commodity(BaseModel):
    description: str
    countryOfManufacture: str
    harmonizedCode: str
    weight: Weight
    quantity: str
    quantityUnits: str
    unitPrice: UnitPrice
    customsValue: CustomsValue

class CustomsClearanceDetail(BaseModel):
    dutiesPayment: DutiesPayment
    commercialInvoice: CommercialInvoice
    isDocumentOnly: bool
    totalCustomsValue: TotalCustomsValue
    _Comment_: str
    commodities: List[Commodity]

class Disposition(BaseModel):
    dispositionType: str

class DocumentFormat(BaseModel):
    stockType: str
    dispositions: List[Disposition]
    docType: str


class CustomerImageUsage(BaseModel):
    id: str
    type: str
    providedImageType: str

class CommercialInvoiceDetail(BaseModel):
    customerImageUsages: List[CustomerImageUsage]
    documentFormat: DocumentFormat

class ShippingDocumentSpecification(BaseModel):
    shippingDocumentTypes: List[str]
    commercialInvoiceDetail: CommercialInvoiceDetail
    


class EtdDetail(BaseModel):
    requestedDocumentTypes: List[str]

class ShipmentSpecialServices(BaseModel):
    specialServiceTypes: List[str]
    etdDetail: EtdDetail



class EmailAggregationType(str, Enum):
    Per_Package = "PER_PACKAGE"
    Per_Shipment = "PER_SHIPMENT"


class EmailNotificationRecipientType(str, Enum):
    Broker = "BROKER"
    Other = "OTHER"
    Recipient = "RECIPIENT"
    Shipper = "SHIPPER"
    Third_Party = "THIRD_PARTY"


class NotificationFormatType(str, Enum):
    HTML = "HTML"
    Text = "TEXT"

class NotificationEventType(str, Enum):
    ON_DELIVERY = "ON_DELIVERY"
    ON_EXCEPTION = "ON_EXCEPTION"
    ON_SHIPMENT = "ON_SHIPMENT"
    ON_TENDER = "ON_TENDER"
    ON_ESTIMATED_DELIVERY = "ON_ESTIMATED_DELIVERY"
    ON_LABEL = "ON_LABEL"
    ON_PICKUP_DRIVER_ARRIVED = "ON_PICKUP_DRIVER_ARRIVED"
    ON_PICKUP_DRIVER_ASSIGNED = "ON_PICKUP_DRIVER_ASSIGNED"
    ON_PICKUP_DRIVER_DEPARTED = "ON_PICKUP_DRIVER_DEPARTED"
    ON_PICKUP_DRIVER_EN_ROUTE = "ON_PICKUP_DRIVER_EN_ROUTE"

class EmailNotificationRecipient(BaseModel):
    name: Optional[str]
    emailNotificationRecipientType: EmailNotificationRecipientType
    emailAddress: str
    notificationFormatType: Optional[NotificationFormatType]
    notificationType: str = "EMAIL"
    locale: str = "tr_TR"
    notificationEventType: List[NotificationEventType]
    
    class Config:
        use_enum_values = True
        validate_all = True
        
    
    
class EmailNotificationDetail(BaseModel):
    aggregationType: EmailAggregationType = EmailAggregationType.Per_Package
    emailNotificationRecipients: List[EmailNotificationRecipient]
    personalMessage: str
    
    class Config:
        use_enum_values = True
        validate_all = True

class RequestedShipment(BaseModel):
    """
    Args:
        `shipDatestamp` (`Optional[str]`): Ship Date. Format: Format [YYYY-MM-DD]
        
        `totalDeclaredValue` (`Optional[TotalDeclaredValue]`): Sum of all declared values of all packages in a shipment

        
    """
    shipDatestamp: Optional[str]
    blockInsightVisibility: bool = False
    
    totalDeclaredValue: Optional[TotalDeclaredValue]
    shipper: Shipper
    soldTo: Optional[SoldTo]
    shipmentSpecialServices: ShipmentSpecialServices
    recipients: List[Recipient]
    recipientLocationNumber: str = ""
    pickupType: PickUpType = PickUpType.Contact_Fedex_To_Schedule
    serviceType: str = "FEDEX_INTERNATIONAL_PRIORITY"
    packagingType: PackagingType = PackagingType.Your_Packaging
    totalWeight: Optional[float]
    origin: Optional[Origin]
    shippingChargesPayment: ShippingChargesPayment
    totalPackageCount: Optional[int]
    requestedPackageLineItems: List[RequestedPackageLineItem]
    labelSpecification: LabelSpecification
    customsClearanceDetail: CustomsClearanceDetail
    shippingDocumentSpecification: ShippingDocumentSpecification
    emailNotificationDetail: Optional[EmailNotificationDetail]
    class Config:
        use_enum_values = True
        validate_all = True
    
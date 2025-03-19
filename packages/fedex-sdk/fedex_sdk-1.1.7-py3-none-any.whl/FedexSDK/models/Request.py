

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from pydantic import BaseModel

from .AccountNumber import AccountNumber

from .RequestedShipment import RequestedShipment


class LabelResponseOptions(str, Enum):
    """
    Label – Indicates request is for encoded bytecode.\n
    Url_Only – Indicates label URL request
    """
    Label: str = "LABEL"
    Url_Only: str = "URL_ONLY"


class MergeLabelDocOption(str, Enum): 
    Labels_Only: str = "LABELS_ONLY"
    NONE: str = "NONE"
    Labels_And_Docs: str = "LABELS_AND_DOCS"


class ShipAction(str, Enum):
    Confirm = "CONFIRM"
    Transfer = "TRANSFER"


class ProcessingOptionType(str, Enum):
    Synchronous_Only: str = "SYNCHRONOUS_ONLY"
    Allow_Asynchronous: str = "ALLOW_ASYNCHRONOUS"
    


class Request(BaseModel):
    labelResponseOptions: LabelResponseOptions
    mergeLabelDocOption: MergeLabelDocOption = MergeLabelDocOption.Labels_Only
    accountNumber: AccountNumber
    shipAction: Optional[ShipAction]
    processingOptionType: ProcessingOptionType = ProcessingOptionType.Synchronous_Only
    oneLabelAtTime: bool = False
    requestedShipment: RequestedShipment

    _Comment_: str = ""
    
    class Config:
        use_enum_values = True
        validate_all = True
    
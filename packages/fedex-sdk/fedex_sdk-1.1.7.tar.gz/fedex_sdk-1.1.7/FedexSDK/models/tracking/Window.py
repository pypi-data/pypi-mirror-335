from pydantic import BaseModel
from typing import Dict, Any, Optional

class Window(BaseModel):
    ends: Optional[str]


class StandardTransitTimeWindow(BaseModel):
    window: Window


class EstimatedDeliveryTimeWindow(BaseModel):
    window: Dict[str, Any]
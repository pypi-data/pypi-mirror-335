from pydantic import BaseModel
from typing import Optional

class DelayDetail(BaseModel):
    status: Optional[str]
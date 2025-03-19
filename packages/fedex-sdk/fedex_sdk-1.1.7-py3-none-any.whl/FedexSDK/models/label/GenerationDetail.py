from pydantic import BaseModel
from typing import Optional


class GenerationDetail(BaseModel):
    type: str
    minimumCopiesRequired: int
    letterhead: Optional[str] = None
    electronicSignature: Optional[str] = None
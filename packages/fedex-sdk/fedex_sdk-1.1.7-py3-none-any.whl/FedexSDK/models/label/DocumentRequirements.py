from typing import List
from .GenerationDetail import GenerationDetail
from pydantic import BaseModel



class DocumentRequirements(BaseModel):
    requiredDocuments: List[str]
    generationDetails: List[GenerationDetail]
    prohibitedDocuments: List[str]
from typing import List
from .UploadDocumentReferenceDetail import UploadDocumentReferenceDetail
from pydantic import BaseModel


class CompletedEtdDetail(BaseModel):
    folderId: str
    type: str
    uploadDocumentReferenceDetails: List[UploadDocumentReferenceDetail]
    
    
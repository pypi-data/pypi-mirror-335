from pydantic import BaseModel

class UploadDocumentReferenceDetail(BaseModel):
    documentType: str
    documentId: str



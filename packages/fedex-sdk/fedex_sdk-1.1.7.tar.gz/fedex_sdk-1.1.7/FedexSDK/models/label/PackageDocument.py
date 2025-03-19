from pydantic import BaseModel

class PackageDocument(BaseModel):
    contentType: str
    copiesToPrint: int
    encodedLabel: str
    docType: str
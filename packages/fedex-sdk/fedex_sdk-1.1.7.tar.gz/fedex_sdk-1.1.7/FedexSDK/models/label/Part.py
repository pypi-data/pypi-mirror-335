from pydantic import BaseModel

class Part(BaseModel):
    documentPartSequenceNumber: int
    image: str
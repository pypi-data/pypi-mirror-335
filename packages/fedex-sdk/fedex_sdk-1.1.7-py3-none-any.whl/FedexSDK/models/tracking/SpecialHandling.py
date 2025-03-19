from pydantic import BaseModel

class SpecialHandling(BaseModel):
    type: str
    description: str
    paymentType: str
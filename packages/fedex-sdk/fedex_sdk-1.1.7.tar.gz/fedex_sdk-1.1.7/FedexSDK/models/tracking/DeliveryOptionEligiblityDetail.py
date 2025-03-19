from pydantic import BaseModel

class DeliveryOptionEligibilityDetail(BaseModel):
    option: str
    eligibility: str

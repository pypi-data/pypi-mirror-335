from pydantic import BaseModel


class ServiceDetail(BaseModel):
    type: str
    description: str
    shortDescription: str
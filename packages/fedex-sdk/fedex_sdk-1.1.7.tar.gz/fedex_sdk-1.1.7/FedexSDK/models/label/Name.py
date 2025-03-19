from pydantic import BaseModel

class Name(BaseModel):
    type: str
    encoding: str
    value: str


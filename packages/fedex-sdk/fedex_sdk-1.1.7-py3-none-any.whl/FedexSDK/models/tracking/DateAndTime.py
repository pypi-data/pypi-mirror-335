from pydantic import BaseModel

class DateAndTime(BaseModel):
    type: str
    dateTime: str
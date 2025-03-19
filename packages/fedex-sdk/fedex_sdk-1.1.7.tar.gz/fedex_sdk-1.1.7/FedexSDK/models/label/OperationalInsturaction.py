from pydantic import BaseModel
class OperationalInstruction(BaseModel):
    number: int
    content: str
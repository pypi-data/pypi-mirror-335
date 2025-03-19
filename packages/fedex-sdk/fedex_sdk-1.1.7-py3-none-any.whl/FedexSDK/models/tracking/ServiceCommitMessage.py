from pydantic import BaseModel

class ServiceCommitMessage(BaseModel):
    message: str
    type: str
from pydantic import BaseModel


class Error(BaseModel):
    type: str
    message: str
    code: int

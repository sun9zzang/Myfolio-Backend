from datetime import datetime

from pydantic import BaseModel


class JWTMetadata(BaseModel):
    exp: datetime
    sub: str

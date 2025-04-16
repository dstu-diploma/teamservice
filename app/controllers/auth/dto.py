from pydantic import BaseModel
from datetime import datetime


class AccessJWTPayloadDto(BaseModel):
    user_id: int
    role: str
    exp: datetime

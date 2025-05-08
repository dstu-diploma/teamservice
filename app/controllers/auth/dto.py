from app.acl.roles import UserRoles
from pydantic import BaseModel
from datetime import datetime


class AccessJWTPayloadDto(BaseModel):
    user_id: int
    role: UserRoles
    exp: datetime

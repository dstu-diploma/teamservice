from app.acl.roles import UserRoles
from pydantic import BaseModel
from datetime import datetime
from enum import StrEnum


class UserUploadsType(StrEnum):
    Avatar = "avatar"
    Cover = "cover"


class UserUploadDto(BaseModel):
    user_id: int
    type: UserUploadsType
    s3_key: str
    content_type: str
    uploaded_at: datetime
    url: str | None


class ExternalUserDto(BaseModel):
    id: int
    is_banned: bool
    formatted_name: str
    role: UserRoles
    uploads: list[UserUploadDto] | None = None

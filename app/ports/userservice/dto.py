from datetime import datetime
from pydantic import BaseModel
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
    role: str
    uploads: list[UserUploadDto] | None = None

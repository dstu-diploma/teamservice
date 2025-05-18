from pydantic import BaseModel


class ExternalUserDto(BaseModel):
    id: int
    is_banned: bool
    formatted_name: str
    role: str

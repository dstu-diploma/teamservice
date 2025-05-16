from pydantic import BaseModel
from datetime import datetime


class MinimalUserDto(BaseModel):
    id: int
    first_name: str
    last_name: str
    patronymic: str
    register_date: datetime
    is_banned: bool

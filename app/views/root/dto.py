from typing import Annotated
from pydantic import BaseModel, StringConstraints


class TeamNameDto(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3, max_length=40)]


class UserIdDto(BaseModel):
    user_id: int

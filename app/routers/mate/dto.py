from pydantic import BaseModel, StringConstraints
from typing import Annotated


class MateCaptainRightsDto(BaseModel):
    user_id: int
    is_captain: bool


class MateRoleDescDto(BaseModel):
    role_desc: Annotated[str, StringConstraints(min_length=2, max_length=35)]

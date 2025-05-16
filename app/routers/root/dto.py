from pydantic import BaseModel, StringConstraints
from typing import Annotated


class TeamNameDto(BaseModel):
    name: Annotated[str, StringConstraints(min_length=3, max_length=40)]

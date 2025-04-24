from pydantic import BaseModel


class ChangeNameDto(BaseModel):
    team_id: int
    new_name: str

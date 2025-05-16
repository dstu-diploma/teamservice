from pydantic import BaseModel


class ChangeNameDto(BaseModel):
    team_id: int
    new_name: str


class AdminMateCaptainRightsDto(BaseModel):
    is_captain: bool


class AdminAddMateDto(BaseModel):
    team_id: int

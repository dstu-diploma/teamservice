from app.models.team import TeamModel
from pydantic import BaseModel


class TeamDto(BaseModel):
    id: int
    name: str
    owner_id: int

    @staticmethod
    def from_tortoise(team: TeamModel):
        return TeamDto(id=team.id, name=team.name, owner_id=team.owner_id)

from app.models.team import TeamMatesModel, TeamModel
from pydantic import BaseModel


class TeamDto(BaseModel):
    id: int
    name: str
    owner_id: int

    @staticmethod
    def from_tortoise(team: TeamModel):
        return TeamDto(id=team.id, name=team.name, owner_id=team.owner_id)


class TeamMateDto(BaseModel):
    user_id: int

    @staticmethod
    def from_tortoise(mate: TeamMatesModel):
        return TeamMateDto(user_id=mate.user_id)

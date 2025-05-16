from app.services.mate.dto import TeamMateDto
from app.models.team import TeamModel
from pydantic import BaseModel


class TeamDto(BaseModel):
    id: int
    name: str

    @staticmethod
    def from_tortoise(team: TeamModel):
        return TeamDto(id=team.id, name=team.name)


class TeamWithMatesDto(TeamDto):
    mates: list[TeamMateDto]

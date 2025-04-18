from app.models.team import TeamMatesModel
from pydantic import BaseModel


class TeamMateDto(BaseModel):
    team_id: int
    user_id: int

    @staticmethod
    def from_tortoise(mate: TeamMatesModel):
        return TeamMateDto(team_id=mate.team_id, user_id=mate.user_id)

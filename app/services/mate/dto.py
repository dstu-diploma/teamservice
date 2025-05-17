from app.models.team import TeamMatesModel
from pydantic import BaseModel


class TeamMateDto(BaseModel):
    team_id: int
    user_id: int
    user_name: str | None = None
    is_captain: bool
    role_desc: str | None

    @staticmethod
    def from_tortoise(mate: TeamMatesModel):
        return TeamMateDto(
            # на самом деле там есть этот атрибут
            team_id=mate.team_id,  # type: ignore[attr-defined]
            user_id=mate.user_id,
            is_captain=mate.is_captain,
            role_desc=mate.role_desc,
        )

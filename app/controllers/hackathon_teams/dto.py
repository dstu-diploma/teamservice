from app.models.hackathon_team import (
    HackathonTeamMatesModel,
    HackathonTeamModel,
)
from pydantic import BaseModel


class HackathonTeamDto(BaseModel):
    id: int
    hackathon_id: int
    name: str

    @staticmethod
    def from_tortoise(team: HackathonTeamModel):
        return HackathonTeamDto(
            id=team.id, name=team.name, hackathon_id=team.hackathon_id
        )


class HackathonTeamMateDto(BaseModel):
    team_id: int
    user_id: int
    is_captain: bool
    role_desc: str | None

    @staticmethod
    def from_tortoise(mate: HackathonTeamMatesModel):
        return HackathonTeamMateDto(
            # на самом деле там есть этот атрибут
            team_id=mate.team_id,  # type: ignore[attr-defined]
            user_id=mate.user_id,
            is_captain=mate.is_captain,
            role_desc=mate.role_desc,
        )


class HackathonTeamWithMatesDto(HackathonTeamDto):
    mates: list[HackathonTeamMateDto]

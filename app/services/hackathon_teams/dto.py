from app.ports.userservice.dto import UserUploadDto
from pydantic import BaseModel

from app.models.hackathon_team import (
    HackathonTeamMatesModel,
    HackathonTeamModel,
)


class HackathonTeamDto(BaseModel):
    id: int
    hackathon_id: int
    name: str
    hackathon_name: str | None = None
    submission_url: str | None = None

    @staticmethod
    def from_tortoise(
        team: HackathonTeamModel,
        submission_url: str | None = None,
        hackathon_name: str | None = None,
    ):
        return HackathonTeamDto(
            id=team.id,
            name=team.name,
            hackathon_id=team.hackathon_id,
            submission_url=submission_url,
            hackathon_name=hackathon_name,
        )


class HackathonTeamMateDto(BaseModel):
    team_id: int
    user_id: int
    user_name: str | None = None
    user_uploads: list[UserUploadDto] | None = None
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

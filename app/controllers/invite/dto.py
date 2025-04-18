from app.models.team import TeamInvitesModel
from pydantic import BaseModel


class TeamInviteDto(BaseModel):
    team_id: int
    user_id: int

    @staticmethod
    def from_tortoise(invite: TeamInvitesModel):
        return TeamInviteDto(team_id=invite.team_id, user_id=invite.user_id)

from app.services.brand_team.interface import ITeamService
from app.services.mate.interface import IMateService
from app.ports.userservice import IUserServicePort
from app.services.invite.dto import TeamInviteDto
from typing import Protocol


class IInviteService(Protocol):
    team_service: ITeamService
    user_service: IUserServicePort
    mate_service: IMateService

    async def clear_by_user(self, user_id: int) -> None: ...
    async def invite_user(
        self, team_id: int, user_id: int
    ) -> TeamInviteDto: ...
    async def get_user_invites(self, user_id: int) -> list[TeamInviteDto]: ...
    async def decline(self, team_id: int, user_id: int) -> None: ...
    async def accept(self, team_id: int, user_id: int) -> None: ...

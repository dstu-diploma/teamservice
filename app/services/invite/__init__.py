from .exceptions import UserAlreadyInvitedException, NoSuchInviteException
from app.services.mate.exceptions import AlreadyTeamMemberException
from app.services.user.exceptions import UserDoesNotExistException
from app.services.user import IUserService
from app.models.team import TeamInvitesModel
from functools import lru_cache
from .dto import TeamInviteDto
from typing import Protocol
from fastapi import Depends

from app.services.team import (
    get_team_service,
    ITeamService,
)
from app.services.mate import (
    get_mate_service,
    IMateService,
)


class IInviteService(Protocol):
    team_service: ITeamService
    user_service: IUserService
    mate_service: IMateService

    async def clear_by_user(self, user_id: int) -> None: ...
    async def invite_user(
        self, team_id: int, user_id: int
    ) -> TeamInviteDto: ...
    async def get_user_invites(self, user_id: int) -> list[TeamInviteDto]: ...
    async def decline(self, team_id: int, user_id: int) -> None: ...
    async def accept(self, team_id: int, user_id: int) -> None: ...


class InviteService(IInviteService):
    def __init__(
        self,
        team_service: ITeamService,
        user_service: IUserService,
        mate_service: IMateService,
    ):
        self.team_service = team_service
        self.user_service = user_service
        self.mate_service = mate_service

    async def clear_by_user(self, user_id: int) -> None:
        await TeamInvitesModel.filter(user_id=user_id).delete()

    async def invite_user(self, team_id: int, user_id: int) -> TeamInviteDto:
        if not await self.user_service.get_user_exists(user_id):
            raise UserDoesNotExistException()

        if await TeamInvitesModel.exists(team_id=team_id, user_id=user_id):
            raise UserAlreadyInvitedException()

        if await self.mate_service.get_mate(user_id):
            raise AlreadyTeamMemberException()

        invite = await TeamInvitesModel.create(team_id=team_id, user_id=user_id)
        return TeamInviteDto.from_tortoise(invite)

    async def get_user_invites(self, user_id: int) -> list[TeamInviteDto]:
        invites = await TeamInvitesModel.filter(user_id=user_id)
        return [TeamInviteDto.from_tortoise(invite) for invite in invites]

    async def decline(self, team_id: int, user_id: int) -> None:
        invite = await TeamInvitesModel.get_or_none(
            team_id=team_id, user_id=user_id
        )

        if invite is None:
            raise NoSuchInviteException()

        await invite.delete()

    # разница между accept и decline только в том, что пользователя реально делает тиммейтом
    # поэтому упрощаем
    async def accept(self, team_id: int, user_id: int) -> None:
        await self.decline(team_id, user_id)
        await self.mate_service.add(team_id, user_id, is_captain=False)
        await self.clear_by_user(user_id)


@lru_cache
def get_invite_service(
    team_service: ITeamService = Depends(get_team_service),
    mate_service: IMateService = Depends(get_mate_service),
) -> InviteService:
    return InviteService(
        team_service=team_service,
        user_service=team_service.user_service,
        mate_service=mate_service,
    )

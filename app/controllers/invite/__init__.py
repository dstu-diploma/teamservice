from .exceptions import UserAlreadyInvitedException, NoSuchInviteException
from app.controllers.mate.exceptions import AlreadyTeamMemberException
from app.controllers.user.exceptions import UserDoesNotExistException
from app.controllers.user import IUserController
from app.models.team import TeamInvitesModel
from functools import lru_cache
from .dto import TeamInviteDto
from typing import Protocol
from fastapi import Depends

from app.controllers.team import (
    get_team_controller,
    ITeamController,
)
from app.controllers.mate import (
    get_mate_controller,
    IMateController,
)


class IInviteController(Protocol):
    team_controller: ITeamController
    user_controller: IUserController
    mate_controller: IMateController

    async def clear_by_user(self, user_id: int) -> None: ...
    async def invite_user(
        self, team_id: int, user_id: int
    ) -> TeamInviteDto: ...
    async def get_user_invites(self, user_id: int) -> list[TeamInviteDto]: ...
    async def decline(self, team_id: int, user_id: int) -> None: ...
    async def accept(self, team_id: int, user_id: int) -> None: ...


class InviteController(IInviteController):
    def __init__(
        self,
        team_controller: ITeamController,
        user_controller: IUserController,
        mate_controller: IMateController,
    ):
        self.team_controller = team_controller
        self.user_controller = user_controller
        self.mate_controller = mate_controller

    async def clear_by_user(self, user_id: int) -> None:
        await TeamInvitesModel.filter(user_id=user_id).delete()

    async def invite_user(self, team_id: int, user_id: int) -> TeamInviteDto:
        if not await self.user_controller.get_user_exists(user_id):
            raise UserDoesNotExistException()

        if await TeamInvitesModel.exists(team_id=team_id, user_id=user_id):
            raise UserAlreadyInvitedException()

        if await self.mate_controller.get_mate(user_id):
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
        await self.mate_controller.add(team_id, user_id, is_captain=False)
        await self.clear_by_user(user_id)


@lru_cache
def get_invite_controller(
    team_controller: ITeamController = Depends(get_team_controller),
    mate_controller: IMateController = Depends(get_mate_controller),
) -> InviteController:
    return InviteController(
        team_controller=team_controller,
        user_controller=team_controller.user_controller,
        mate_controller=mate_controller,
    )

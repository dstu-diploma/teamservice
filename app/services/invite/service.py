from app.ports.userservice.exceptions import UserDoesNotExistException
from app.services.mate.exceptions import AlreadyTeamMemberException
from app.services.brand_team.interface import ITeamService
from app.services.invite.interface import IInviteService
from app.services.mate.interface import IMateService
from app.ports.userservice import IUserServicePort
from app.services.invite.dto import TeamInviteDto
from app.models.team import TeamInvitesModel

from app.services.invite.exceptions import (
    NoSuchInviteException,
    UserAlreadyInvitedException,
)


class InviteService(IInviteService):
    def __init__(
        self,
        team_service: ITeamService,
        user_service: IUserServicePort,
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

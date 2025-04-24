from app.controllers.user import (
    IUserController,
    UserController,
    get_user_controller,
)
from .exceptions import AlreadyTeamMemberException, NotAMemberException
from app.controllers.user.exceptions import UserDoesNotExistException
from app.models.team import TeamMatesModel
from .dto import TeamMateDto
from typing import Protocol
from fastapi import Depends


class IMateController(Protocol):
    user_controller: IUserController

    async def get_mates(self, team_id: int) -> list[TeamMateDto]: ...
    async def get_mate(self, user_id: int) -> TeamMateDto | None: ...
    async def add(self, team_id: int, user_id: int) -> TeamMateDto: ...
    async def remove(self, user_id: int) -> None: ...


class MateController(IMateController):
    def __init__(self, user_controller: IUserController):
        self.user_controller = user_controller

    async def get_mate(self, user_id: int) -> TeamMateDto | None:
        mate = await TeamMatesModel.get_or_none(user_id=user_id)
        if mate:
            return TeamMateDto.from_tortoise(mate)
        return None

    async def get_mates(self, team_id: int) -> list[TeamMateDto]:
        mates = await TeamMatesModel.filter(team_id=team_id)

        return [TeamMateDto.from_tortoise(mate) for mate in mates]

    async def add(self, team_id: int, user_id: int) -> TeamMateDto:
        if not await self.user_controller.get_user_exists(user_id):
            raise UserDoesNotExistException()

        if await self.get_mate(user_id) is not None:
            raise AlreadyTeamMemberException()

        mate = await TeamMatesModel.create(team_id=team_id, user_id=user_id)
        return TeamMateDto.from_tortoise(mate)

    async def remove(self, user_id: int) -> None:
        if not await self.user_controller.get_user_exists(user_id):
            raise UserDoesNotExistException()

        mate = await TeamMatesModel.get_or_none(user_id=user_id)
        if mate is None:
            raise NotAMemberException()

        await mate.delete()


def get_mate_controller(
    user_controller: UserController = Depends(get_user_controller),
) -> MateController:
    return MateController(user_controller)

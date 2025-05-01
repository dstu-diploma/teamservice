from .exceptions import AlreadyTeamMemberException, NotAMemberException
from app.controllers.user.exceptions import UserDoesNotExistException
from app.models.team import TeamMatesModel
from functools import lru_cache
from .dto import TeamMateDto
from typing import Protocol
from fastapi import Depends

from app.controllers.user import (
    get_user_controller,
    IUserController,
)


class IMateController(Protocol):
    user_controller: IUserController

    async def get_mate(self, user_id: int) -> TeamMateDto | None: ...
    async def get_mates(self, team_id: int) -> list[TeamMateDto]: ...
    async def add(
        self, team_id: int, user_id: int, is_captain: bool
    ) -> TeamMateDto: ...
    async def remove(self, user_id: int) -> None: ...
    async def set_is_captain(
        self, user_id: int, is_captain: bool
    ) -> TeamMateDto: ...
    async def get_captains(self, team_id: int) -> list[TeamMateDto]: ...


class MateController(IMateController):
    def __init__(self, user_controller: IUserController):
        self.user_controller = user_controller

    async def _get_mate(self, user_id: int) -> TeamMatesModel:
        mate = await TeamMatesModel.get_or_none(user_id=user_id)
        if mate is None:
            raise NotAMemberException()

        return mate

    async def get_mate(self, user_id: int) -> TeamMateDto | None:
        mate = await TeamMatesModel.get_or_none(user_id=user_id)
        if mate:
            return TeamMateDto.from_tortoise(mate)
        return None

    async def get_mates(self, team_id: int) -> list[TeamMateDto]:
        mates = await TeamMatesModel.filter(team_id=team_id)

        return [TeamMateDto.from_tortoise(mate) for mate in mates]

    async def add(
        self, team_id: int, user_id: int, is_captain: bool
    ) -> TeamMateDto:
        if not await self.user_controller.get_user_exists(user_id):
            raise UserDoesNotExistException()

        if await self.get_mate(user_id) is not None:
            raise AlreadyTeamMemberException()

        mate = await TeamMatesModel.create(
            team_id=team_id, user_id=user_id, is_captain=is_captain
        )
        return TeamMateDto.from_tortoise(mate)

    async def remove(self, user_id: int) -> None:
        if not await self.user_controller.get_user_exists(user_id):
            raise UserDoesNotExistException()

        mate = await self._get_mate(user_id)
        await mate.delete()

    async def set_is_captain(
        self, user_id: int, is_captain: bool
    ) -> TeamMateDto:
        if not await self.user_controller.get_user_exists(user_id):
            raise UserDoesNotExistException()

        mate = await self._get_mate(user_id)
        mate.is_captain = is_captain
        await mate.save()

        return TeamMateDto.from_tortoise(mate)

    async def get_captains(self, team_id: int) -> list[TeamMateDto]:
        captains = await TeamMatesModel.filter(team_id=team_id, is_captain=True)
        return [TeamMateDto.from_tortoise(captain) for captain in captains]


@lru_cache
def get_mate_controller(
    user_controller: IUserController = Depends(get_user_controller),
) -> MateController:
    return MateController(user_controller)

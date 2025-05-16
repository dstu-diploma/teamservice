from .exceptions import AlreadyTeamMemberException, NotAMemberException
from app.services.user.exceptions import UserDoesNotExistException
from app.models.team import TeamMatesModel
from functools import lru_cache
from .dto import TeamMateDto
from typing import Protocol
from fastapi import Depends

from app.services.user import (
    get_user_service,
    IUserService,
)


class IMateService(Protocol):
    user_service: IUserService

    async def get_mate(self, user_id: int) -> TeamMateDto | None: ...
    async def get_mates(self, team_id: int) -> list[TeamMateDto]: ...
    async def get_mate_count(self, team_id: int) -> int: ...
    async def add(
        self,
        team_id: int,
        user_id: int,
        is_captain: bool,
    ) -> TeamMateDto: ...
    async def remove(self, user_id: int) -> TeamMateDto: ...
    async def set_is_captain(
        self, user_id: int, is_captain: bool
    ) -> TeamMateDto: ...
    async def set_role_desc(
        self, user_id: int, role_desc: str
    ) -> TeamMateDto: ...
    async def get_captains(self, team_id: int) -> list[TeamMateDto]: ...


class MateService(IMateService):
    def __init__(self, user_service: IUserService):
        self.user_service = user_service

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

    async def get_mate_count(self, team_id: int) -> int:
        return await TeamMatesModel.filter(team_id=team_id).count()

    async def add(
        self, team_id: int, user_id: int, is_captain: bool
    ) -> TeamMateDto:
        if not await self.user_service.get_user_exists(user_id):
            raise UserDoesNotExistException()

        if await self.get_mate(user_id) is not None:
            raise AlreadyTeamMemberException()

        mate = await TeamMatesModel.create(
            team_id=team_id, user_id=user_id, is_captain=is_captain
        )
        return TeamMateDto.from_tortoise(mate)

    async def remove(self, user_id: int) -> TeamMateDto:
        if not await self.user_service.get_user_exists(user_id):
            raise UserDoesNotExistException()

        mate = await self._get_mate(user_id)
        await mate.delete()
        return TeamMateDto.from_tortoise(mate)

    async def set_is_captain(
        self, user_id: int, is_captain: bool
    ) -> TeamMateDto:
        if not await self.user_service.get_user_exists(user_id):
            raise UserDoesNotExistException()

        mate = await self._get_mate(user_id)
        mate.is_captain = is_captain
        await mate.save()

        return TeamMateDto.from_tortoise(mate)

    async def set_role_desc(self, user_id: int, role_desc: str) -> TeamMateDto:
        if not await self.user_service.get_user_exists(user_id):
            raise UserDoesNotExistException()

        mate = await self._get_mate(user_id)
        mate.role_desc = role_desc
        await mate.save()

        return TeamMateDto.from_tortoise(mate)

    async def get_captains(self, team_id: int) -> list[TeamMateDto]:
        captains = await TeamMatesModel.filter(team_id=team_id, is_captain=True)
        return [TeamMateDto.from_tortoise(captain) for captain in captains]


@lru_cache
def get_mate_service(
    user_service: IUserService = Depends(get_user_service),
) -> MateService:
    return MateService(user_service)

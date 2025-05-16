from app.services.mate.exceptions import AlreadyTeamMemberException
from app.services.user.exceptions import UserDoesNotExistException
from app.services.team.dto import TeamDto, TeamWithMatesDto
from tortoise.exceptions import IntegrityError
from app.models.team import TeamModel
from functools import lru_cache
from fastapi import Depends
from typing import Protocol

from app.services.team.exceptions import (
    TeamNameAlreadyUsedException,
    TeamDoesNotExistException,
    UserIsNotOwnerOfTeamException,
    UserNotInTeamException,
)
from app.services.user import (
    IUserService,
    get_user_service,
)

from app.services.mate import (
    IMateService,
    get_mate_service,
)


class ITeamService(Protocol):
    user_service: IUserService
    mate_service: IMateService

    async def exists(self, team_id: int) -> bool: ...
    async def create(self, name: str, owner_id: int) -> TeamDto: ...
    async def get_info(self, team_id: int) -> TeamWithMatesDto: ...
    async def update_name(self, team_id: int, new_name: str) -> TeamDto: ...
    async def delete(self, team_id: int) -> None: ...
    async def get_by_mate(self, user_id: int) -> TeamWithMatesDto: ...
    async def get_by_captain(self, captain_id: int) -> TeamDto: ...
    async def get_all(self) -> list[TeamDto]: ...


class TeamService(ITeamService):
    def __init__(self, user_service: IUserService, mate_service: IMateService):
        self.user_service = user_service
        self.mate_service = mate_service

    async def _get_team_by_id(self, team_id: int) -> TeamModel:
        team = await TeamModel.get_or_none(id=team_id)

        if team is None:
            raise TeamDoesNotExistException()

        return team

    async def exists(self, team_id: int) -> bool:
        return await TeamModel.exists(id=team_id)

    async def create(self, name: str, owner_id: int) -> TeamDto:
        if not await self.user_service.get_user_exists(owner_id):
            raise UserDoesNotExistException()

        if await self.mate_service.get_mate(owner_id) is not None:
            raise AlreadyTeamMemberException()

        try:
            team = await TeamModel.create(name=name, owner_id=owner_id)
            await self.mate_service.add(team.id, owner_id, is_captain=True)
            return TeamDto.from_tortoise(team)
        except IntegrityError as e:
            raise TeamNameAlreadyUsedException from e

    async def get_info(self, team_id: int) -> TeamWithMatesDto:
        team = await self._get_team_by_id(team_id)
        mates = await self.mate_service.get_mates(team_id)

        return TeamWithMatesDto(id=team.id, name=team.name, mates=mates)

    async def update_name(self, team_id: int, new_name: str) -> TeamDto:
        team = await self._get_team_by_id(team_id)
        team.name = new_name

        try:
            await team.save()
            return TeamDto.from_tortoise(team)
        except IntegrityError as e:
            raise TeamNameAlreadyUsedException from e

    async def delete(self, team_id: int) -> None:
        team = await self._get_team_by_id(team_id)
        await team.delete()

    async def get_by_mate(self, user_id: int) -> TeamWithMatesDto:
        mate = await self.mate_service.get_mate(user_id)

        if mate is None:
            raise UserNotInTeamException()

        return await self.get_info(mate.team_id)

    async def get_by_captain(self, captain_id: int) -> TeamDto:
        mate = await self.mate_service.get_mate(captain_id)

        if mate is None:
            raise UserNotInTeamException()

        if not mate.is_captain:
            raise UserIsNotOwnerOfTeamException()

        team = await self._get_team_by_id(mate.team_id)
        return TeamDto.from_tortoise(team)

    async def get_all(self) -> list[TeamDto]:
        teams = await TeamModel.all()
        return [TeamDto.from_tortoise(team) for team in teams]


@lru_cache
def get_team_service(
    user_service: IUserService = Depends(get_user_service),
    mate_service: IMateService = Depends(get_mate_service),
) -> TeamService:
    return TeamService(user_service, mate_service)

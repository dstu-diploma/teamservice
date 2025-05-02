from app.controllers.mate.exceptions import AlreadyTeamMemberException
from app.controllers.user.exceptions import UserDoesNotExistException
from app.controllers.team.dto import TeamDto, TeamWithMatesDto
from tortoise.exceptions import IntegrityError
from app.models.team import TeamModel
from functools import lru_cache
from fastapi import Depends
from typing import Protocol

from app.controllers.team.exceptions import (
    TeamNameAlreadyUsedException,
    TeamDoesNotExistException,
    UserIsNotOwnerOfTeamException,
    UserNotInTeamException,
)
from app.controllers.user import (
    IUserController,
    get_user_controller,
)

from app.controllers.mate import (
    IMateController,
    get_mate_controller,
)


class ITeamController(Protocol):
    user_controller: IUserController
    mate_controller: IMateController

    async def exists(self, team_id: int) -> bool: ...
    async def create(self, name: str, owner_id: int) -> TeamDto: ...
    async def get_info(self, team_id: int) -> TeamWithMatesDto: ...
    async def update_name(self, team_id: int, new_name: str) -> TeamDto: ...
    async def delete(self, team_id: int) -> None: ...
    async def get_by_mate(self, user_id: int) -> TeamWithMatesDto: ...
    async def get_by_captain(self, captain_id: int) -> TeamDto: ...
    async def get_all(self) -> list[TeamDto]: ...


class TeamController(ITeamController):
    def __init__(
        self, user_controller: IUserController, mate_controller: IMateController
    ):
        self.user_controller = user_controller
        self.mate_controller = mate_controller

    async def _get_team_by_id(self, team_id: int) -> TeamModel:
        team = await TeamModel.get_or_none(id=team_id)

        if team is None:
            raise TeamDoesNotExistException()

        return team

    async def exists(self, team_id: int) -> bool:
        return await TeamModel.exists(id=team_id)

    async def create(self, name: str, owner_id: int) -> TeamDto:
        if not await self.user_controller.get_user_exists(owner_id):
            raise UserDoesNotExistException()

        if await self.mate_controller.get_mate(owner_id) is not None:
            raise AlreadyTeamMemberException()

        try:
            team = await TeamModel.create(name=name, owner_id=owner_id)
            await self.mate_controller.add(team.id, owner_id, is_captain=True)
            return TeamDto.from_tortoise(team)
        except IntegrityError as e:
            raise TeamNameAlreadyUsedException from e

    async def get_info(self, team_id: int) -> TeamWithMatesDto:
        team = await self._get_team_by_id(team_id)
        mates = await self.mate_controller.get_mates(team_id)

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
        mate = await self.mate_controller.get_mate(user_id)

        if mate is None:
            raise UserNotInTeamException()

        return await self.get_info(mate.team_id)

    async def get_by_captain(self, captain_id: int) -> TeamDto:
        mate = await self.mate_controller.get_mate(captain_id)

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
def get_team_controller(
    user_controller: IUserController = Depends(get_user_controller),
    mate_controller: IMateController = Depends(get_mate_controller),
) -> TeamController:
    return TeamController(user_controller, mate_controller)

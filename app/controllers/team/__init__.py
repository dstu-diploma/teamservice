from app.controllers.user.exceptions import UserDoesNotExistException
from app.controllers.team.exceptions import (
    TeamNameAlreadyUsedException,
    AlreadyTeamOwnerException,
    TeamDoesNotExistException,
)
from app.controllers.mate.exceptions import AlreadyTeamMemberException
from app.controllers.user import (
    IUserController,
    UserController,
    get_user_controller,
)
from app.controllers.team.dto import TeamDto
from app.models.team import TeamMatesModel, TeamModel
from fastapi import Depends
from typing import Protocol
from tortoise.exceptions import IntegrityError


class ITeamController(Protocol):
    user_controller: IUserController

    async def create(self, name: str, owner_id: int) -> TeamDto: ...
    async def get_info(self, team_id: int) -> TeamDto: ...
    async def update_name(self, team_id: int, new_name: str) -> TeamDto: ...
    async def delete(self, team_id: int) -> None: ...
    async def get_by_owner(self, owner_id: int) -> TeamDto | None: ...


class TeamController(ITeamController):
    def __init__(self, user_controller: IUserController):
        self.user_controller = user_controller

    async def _get_team_by_id(self, team_id: int) -> TeamModel:
        team = await TeamModel.get_or_none(id=team_id)

        if team is None:
            raise TeamDoesNotExistException()

        return team

    async def create(self, name: str, owner_id: int) -> TeamDto:
        if not await self.user_controller.get_user_exists(owner_id):
            raise UserDoesNotExistException()

        if await self.get_by_owner(owner_id) is not None:
            raise AlreadyTeamOwnerException()

        if await TeamMatesModel.get_or_none(user_id=owner_id) is not None:
            raise AlreadyTeamMemberException()

        try:
            team = await TeamModel.create(name=name, owner_id=owner_id)
            return TeamDto.from_tortoise(team)
        except IntegrityError:
            raise TeamNameAlreadyUsedException from IntegrityError

    async def get_info(self, team_id: int) -> TeamDto:
        return TeamDto.from_tortoise(await self._get_team_by_id(team_id))

    async def update_name(self, team_id: int, new_name: str) -> TeamDto:
        team = await self._get_team_by_id(team_id)
        team.name = new_name

        try:
            await team.save()
            return TeamDto.from_tortoise(team)
        except IntegrityError:
            raise TeamNameAlreadyUsedException from IntegrityError

    async def delete(self, team_id: int) -> None:
        team = await self._get_team_by_id(team_id)
        await team.delete()

    async def get_by_owner(self, owner_id: int) -> TeamDto | None:
        team = await TeamModel.get_or_none(owner_id=owner_id)

        if team:
            return TeamDto.from_tortoise(team)

        return None


def get_team_controller(
    controller: UserController = Depends(get_user_controller),
) -> TeamController:
    return TeamController(controller)

from app.controllers.user.exceptions import UserDoesNotExistException
from app.controllers.team.exceptions import (
    AlreadyTeamMemberException,
    TeamDoesNotExistException,
)
from app.controllers.user import IUserController, UserController
from app.controllers.team.dto import TeamDto, TeamMateDto
from app.models.team import TeamMatesModel, TeamModel
from fastapi import Depends
from typing import Protocol


class ITeamController(Protocol):
    user_controller: IUserController

    async def create(self, name: str, owner_id: int) -> TeamDto: ...
    async def get_info(self, team_id: int) -> TeamDto: ...
    async def get_mates(self, team_id: int) -> list[TeamMateDto]: ...
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

        if TeamMatesModel.get_or_none(user_id=owner_id) is not None:
            raise AlreadyTeamMemberException()

        team = await TeamModel.create(name=name, owner_id=owner_id)
        return TeamDto.from_tortoise(team)

    async def get_info(self, team_id: int) -> TeamDto:
        return TeamDto.from_tortoise(await self._get_team_by_id(team_id))

    async def get_mates(self, team_id: int) -> list[TeamMateDto]:
        mates = await TeamMatesModel.filter(team_id=team_id)

        return [TeamMateDto.from_tortoise(mate) for mate in mates]

    async def update_name(self, team_id: int, new_name: str) -> TeamDto:
        team = await self._get_team_by_id(team_id)
        team.name = new_name
        await team.save()

        return TeamDto.from_tortoise(team)

    async def delete(self, team_id: int) -> None:
        team = await self._get_team_by_id(team_id)
        await team.delete()

    async def get_by_owner(self, owner_id: int) -> TeamDto | None:
        team = await TeamModel.get_or_none(owner_id=owner_id)

        if team:
            return TeamDto.from_tortoise(team)

        return None


def get_team_controller(
    controller: UserController = Depends(UserController),
) -> TeamController:
    return TeamController(controller)

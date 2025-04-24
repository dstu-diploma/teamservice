from app.controllers.mate import (
    IMateController,
    MateController,
    get_mate_controller,
)
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
from app.controllers.team.dto import TeamDto, TeamWithMatesDto
from app.models.team import TeamMatesModel, TeamModel
from fastapi import Depends
from typing import Protocol
from tortoise.exceptions import IntegrityError


class ITeamController(Protocol):
    user_controller: IUserController
    mate_controller: IMateController

    async def create(self, name: str, owner_id: int) -> TeamDto: ...
    async def exists(self, team_id: int) -> bool: ...
    async def get_info(self, team_id: int) -> TeamWithMatesDto: ...
    async def update_name(self, team_id: int, new_name: str) -> TeamDto: ...
    async def delete(self, team_id: int) -> None: ...
    async def get_by_owner(self, owner_id: int) -> TeamDto | None: ...
    async def get_all(self) -> list[TeamDto]: ...
    async def grant_ownership(
        self, team_id: int, new_owner_id: int
    ) -> TeamDto: ...


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

        if await self.get_by_owner(owner_id) is not None:
            raise AlreadyTeamOwnerException()

        if await TeamMatesModel.get_or_none(user_id=owner_id) is not None:
            raise AlreadyTeamMemberException()

        try:
            team = await TeamModel.create(name=name, owner_id=owner_id)
            return TeamDto.from_tortoise(team)
        except IntegrityError:
            raise TeamNameAlreadyUsedException from IntegrityError

    async def get_info(self, team_id: int) -> TeamWithMatesDto:
        team = await self._get_team_by_id(team_id)
        mates = await self.mate_controller.get_mates(team_id)

        return TeamWithMatesDto(
            id=team.id, name=team.name, owner_id=team.owner_id, mates=mates
        )

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

    async def get_all(self) -> list[TeamDto]:
        teams = await TeamModel.all()
        return [TeamDto.from_tortoise(team) for team in teams]

    async def grant_ownership(self, team_id: int, new_owner_id: int) -> TeamDto:
        team = await self._get_team_by_id(team_id)
        await self.mate_controller.remove(new_owner_id)
        await self.mate_controller.add(team_id, team.owner_id)
        team.owner_id = new_owner_id
        await team.save()

        return TeamDto.from_tortoise(team)


def get_team_controller(
    user_controller: UserController = Depends(get_user_controller),
    mate_controller: MateController = Depends(get_mate_controller),
) -> TeamController:
    return TeamController(user_controller, mate_controller)

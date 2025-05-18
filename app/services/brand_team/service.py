from app.ports.userservice.exceptions import UserDoesNotExistException
from app.services.mate.exceptions import AlreadyTeamMemberException
from app.services.brand_team.dto import TeamDto, TeamWithMatesDto
from app.services.brand_team.interface import ITeamService
from app.services.mate.interface import IMateService
from app.ports.userservice import IUserServicePort
from app.events.emitter import Emitter, Events
from tortoise.exceptions import IntegrityError
from app.models.team import TeamModel
from collections import defaultdict

from app.services.brand_team.exceptions import (
    UserIsNotOwnerOfTeamException,
    TeamNameAlreadyUsedException,
    TeamDoesNotExistException,
    UserNotInTeamException,
)


class TeamService(ITeamService):
    def __init__(
        self, user_service: IUserServicePort, mate_service: IMateService
    ):
        self.user_service = user_service
        self.mate_service = mate_service

        self._init_events()

    def _init_events(self):
        async def on_user_deleted(payload: dict):
            user_id = payload["data"]["user_id"]
            mate = await self.mate_service.get_mate(user_id)
            if mate is None:
                return

            await self.mate_service.remove(user_id)

            if await self.mate_service.get_mate_count(mate.team_id) == 0:
                await self.delete(mate.team_id)

        async def on_user_banned(payload: dict):
            is_banned = payload["data"]["is_banned"]
            if is_banned:
                return await on_user_deleted(payload)

        Emitter.on(Events.UserDeleted, on_user_deleted)
        Emitter.on(Events.UserBanned, on_user_banned)

    async def _get_team_by_id(self, team_id: int) -> TeamModel:
        team = await TeamModel.get_or_none(id=team_id)

        if team is None:
            raise TeamDoesNotExistException()

        return team

    async def get_team_by_id(self, team_id: int) -> TeamDto:
        return TeamDto.from_tortoise(await self._get_team_by_id(team_id))

    async def get_name_map(self) -> defaultdict[int, str | None]:
        teams = await TeamModel.all().only("id", "name")
        mapping: defaultdict[int, str | None] = defaultdict(lambda: None)

        for team in teams:
            mapping[team.id] = team.name

        return mapping

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

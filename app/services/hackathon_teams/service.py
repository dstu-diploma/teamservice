from app.services.hackathon_teams.interface import IHackathonTeamsService
from app.services.brand_team.exceptions import TeamDoesNotExistException
from app.ports.hackathonservice import IHackathonServicePort
from app.services.mate.exceptions import NotAMemberException
from app.services.brand_team.interface import ITeamService
from app.ports.event_publisher import IEventPublisherPort
from app.services.mate.interface import IMateService
from app.ports.userservice import IUserServicePort
from tortoise.transactions import in_transaction
from app.events.emitter import Emitter, Events
from app.services.mate.dto import TeamMateDto
import app.util.dto_utils as dto_utils
from typing import cast


from .exceptions import (
    UserAlreadyParticipatingInHackathonException,
    ThisBrandTeamAlreadyParticipatesException,
    CantCreateTeamWithoutCaptainException,
    TeamDoesNotFitHackathonException,
    CantEditHackathonTeamsException,
    CantMakeSuchLargeTeamException,
    CantCreateEmptyTeamException,
    MateTeamMismatchException,
)

from app.services.hackathon_team_submissions.interface import (
    IHackathonTeamSubmissionsService,
)

from .dto import (
    HackathonTeamWithMatesDto,
    HackathonTeamMateDto,
    HackathonTeamDto,
)

from app.models.hackathon_team import (
    HackathonTeamMatesModel,
    HackathonTeamModel,
)


class HackathonTeamsService(IHackathonTeamsService):
    def __init__(
        self,
        hackathon_service: IHackathonServicePort,
        brand_mate_service: IMateService,
        brand_team_service: ITeamService,
        submission_service: IHackathonTeamSubmissionsService,
        user_service: IUserServicePort,
        event_publisher: IEventPublisherPort,
    ):
        self.hackathon_service = hackathon_service
        self.brand_mate_service = brand_mate_service
        self.brand_team_service = brand_team_service
        self.submission_service = submission_service
        self.user_service = user_service
        self.event_publisher = event_publisher

        self._init_events()

    def _init_events(self):
        async def on_user_deleted(payload: dict):
            data: dict | None = payload.get("data", None)
            if data is None:
                return

            user_id = data.get("id")
            if user_id is None:
                return

            mate_data = await HackathonTeamMatesModel.filter(
                user_id=user_id
            ).prefetch_related("team")
            for mate in mate_data:
                try:
                    await self.remove_mate(
                        mate.team.hackathon_id, mate.user_id, silent=True
                    )
                except Exception as e:
                    pass

        async def on_user_banned(payload: dict):
            is_banned = payload["data"]["is_banned"]
            if is_banned:
                return await on_user_deleted(payload)

        async def on_hackathon_deleted(payload: dict):
            data: dict | None = payload.get("data", None)
            if data is None:
                return

            hackathon_id = data.get("id")
            if hackathon_id is None:
                return

            await HackathonTeamModel.filter(hackathon_id=hackathon_id).delete()

        Emitter.on(Events.UserDeleted, on_user_deleted)
        Emitter.on(Events.UserBanned, on_user_banned)
        Emitter.on(Events.HackathonDeleted, on_hackathon_deleted)

    async def get_registered_users_count(self, hackathon_id: int) -> int:
        return await HackathonTeamMatesModel.filter(
            team__hackathon_id=hackathon_id
        ).count()

    async def get_mates(self, team_id: int) -> list[HackathonTeamMateDto]:
        mates = await HackathonTeamMatesModel.filter(team_id=team_id)

        dtos = [HackathonTeamMateDto.from_tortoise(mate) for mate in mates]
        external_user_info = await self.user_service.try_get_user_info_many(
            dto_utils.export_int_fields(dtos, "user_id")
        )
        names = self.user_service.get_name_map(external_user_info)
        user_map = dict((user.id, user) for user in external_user_info)

        dtos = dto_utils.inject_mapping(
            dtos, names, "user_id", "user_name", strict=True
        )

        for dto in dtos:
            if dto.user_id in user_map:
                dto.user_uploads = user_map[dto.user_id].uploads

        return dtos

    async def _get_mate(
        self, user_id: int, hackathon_id: int
    ) -> HackathonTeamMatesModel:
        mate = await HackathonTeamMatesModel.get_or_none(
            user_id=user_id, team__hackathon_id=hackathon_id
        )
        if mate is None:
            raise NotAMemberException()

        return mate

    async def mate_exists(self, user_id: int, hackathon_id: int) -> bool:
        return await HackathonTeamMatesModel.exists(
            user_id=user_id, team__hackathon_id=hackathon_id
        )

    async def get_mate(
        self, user_id: int, hackathon_id: int
    ) -> HackathonTeamMateDto:
        dto = HackathonTeamMateDto.from_tortoise(
            await self._get_mate(user_id, hackathon_id)
        )

        user_info = await self.user_service.try_get_user_info(user_id)
        if user_info:
            dto.user_name = user_info.formatted_name
            dto.user_uploads = user_info.uploads

        return dto

    async def _get_by_id(self, team_id: int) -> HackathonTeamModel:
        team = await HackathonTeamModel.get_or_none(id=team_id)
        if team is None:
            raise TeamDoesNotExistException()

        return team

    async def get_by_id(self, team_id: int) -> HackathonTeamDto:
        team = await self._get_by_id(team_id)
        hack_info = await self.hackathon_service.try_get_hackathon_data(
            team.hackathon_id
        )
        dto = HackathonTeamDto.from_tortoise(
            team,
            submission=await self.submission_service.get_submission(
                team.hackathon_id, team_id
            ),
        )

        if hack_info:
            dto.hackathon_name = hack_info.name

        return dto

    async def get_total(self, team_id: int) -> HackathonTeamWithMatesDto:
        team = await self.get_by_id(team_id)
        mates = await self.get_mates(team_id)

        return HackathonTeamWithMatesDto(
            **team.model_dump(),
            mates=mates,
        )

    async def _validate_hackathon_limits(
        self, hackathon_id: int, mates_count: int
    ):
        hackathon = await self.hackathon_service.get_hackathon_data(
            hackathon_id
        )

        if mates_count > hackathon.max_team_mates_count:
            raise CantMakeSuchLargeTeamException()

        if (
            await self.get_registered_users_count(hackathon_id) + mates_count
            > hackathon.max_participant_count
        ):
            raise TeamDoesNotFitHackathonException()

    async def get_team_by_name_exists(
        self, name: str, hackathon_id: int
    ) -> bool:
        return await HackathonTeamModel.exists(
            name=name, hackathon_id=hackathon_id
        )

    # :skull:
    async def create(
        self, brand_team_id: int, hackathon_id: int, mate_user_ids: list[int]
    ) -> HackathonTeamWithMatesDto:
        if len(mate_user_ids) == 0:
            raise CantCreateEmptyTeamException()

        if not await self.hackathon_service.can_edit_team_registry(
            hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        hackathon_data = await self.hackathon_service.get_hackathon_data(
            hackathon_id
        )

        brand_team = await self.brand_team_service.get_info(brand_team_id)

        if await self.get_team_by_name_exists(brand_team.name, hackathon_id):
            raise ThisBrandTeamAlreadyParticipatesException()

        brand_mates = [
            brand_mate
            for brand_mate in brand_team.mates
            if brand_mate.user_id in mate_user_ids
        ]

        for mate in brand_mates:
            if await self.mate_exists(mate.user_id, hackathon_id):
                raise UserAlreadyParticipatingInHackathonException()

        if len(brand_mates) == 0:
            raise CantCreateEmptyTeamException()

        if not any(
            filter(lambda mate: cast(TeamMateDto, mate).is_captain, brand_mates)
        ):
            raise CantCreateTeamWithoutCaptainException()

        await self._validate_hackathon_limits(hackathon_id, len(brand_mates))

        async with in_transaction():
            hackathon_team = await HackathonTeamModel.create(
                hackathon_id=hackathon_id, name=brand_team.name
            )

            for mate in brand_mates:
                await HackathonTeamMatesModel.create(
                    team_id=hackathon_team.id,
                    user_id=mate.user_id,
                    is_captain=mate.is_captain,
                    role_desc=mate.role_desc,
                )

            return HackathonTeamWithMatesDto(
                id=hackathon_team.id,
                hackathon_id=hackathon_id,
                hackathon_name=hackathon_data.name,
                name=hackathon_team.name,
                mates=await self.get_mates(hackathon_team.id),
            )

    async def set_mate_is_captain(
        self, hackathon_id: int, mate_user_id: int, is_captain: bool
    ) -> HackathonTeamMateDto:
        mate = await self._get_mate(mate_user_id, hackathon_id)

        if not await self.hackathon_service.can_edit_team_registry(
            (await mate.team).hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        mate.is_captain = is_captain
        await mate.save()

        dto = HackathonTeamMateDto.from_tortoise(mate)
        user_info = await self.user_service.try_get_user_info(mate_user_id)
        if user_info:
            dto.user_name = user_info.formatted_name
            dto.user_uploads = user_info.uploads

        return dto

    async def set_mate_role_desc(
        self, hackathon_id: int, mate_user_id: int, role_desc: str
    ) -> HackathonTeamMateDto:
        mate = await self._get_mate(mate_user_id, hackathon_id)

        if not await self.hackathon_service.can_edit_team_registry(
            (await mate.team).hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        mate.role_desc = role_desc
        await mate.save()

        dto = HackathonTeamMateDto.from_tortoise(mate)
        user_info = await self.user_service.try_get_user_info(mate_user_id)
        if user_info:
            dto.user_name = user_info.formatted_name
            dto.user_uploads = user_info.uploads

        return dto

    async def delete_team(self, team_id: int) -> HackathonTeamDto:
        team = await self._get_by_id(team_id)
        await team.delete()
        dto = HackathonTeamDto.from_tortoise(team)

        await self.event_publisher.publish("team.hackathon_team_deleted", dto)

        return dto

    async def remove_mate(
        self, hackathon_id: int, mate_user_id: int, silent: bool = False
    ) -> HackathonTeamMateDto:
        mate = await self._get_mate(mate_user_id, hackathon_id)

        if not await self.hackathon_service.can_edit_team_registry(
            (await mate.team).hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        team_id = cast(int, mate.team_id)  # type: ignore[attr-defined]

        total_mates = await self.get_mates(team_id)
        if len(total_mates) == 1:
            await self.delete_team(team_id)
        else:
            await mate.delete()

        dto = HackathonTeamMateDto.from_tortoise(mate)
        if not silent:
            user_info = await self.user_service.try_get_user_info(mate_user_id)
            if user_info:
                dto.user_name = user_info.formatted_name
                dto.user_uploads = user_info.uploads

        return dto

    async def add_mate(
        self,
        from_brand_team_id: int,
        to_hackathon_team_id: int,
        mate_user_id: int,
    ) -> HackathonTeamMateDto:
        hackathon_team = await self.get_by_id(to_hackathon_team_id)
        if not await self.hackathon_service.can_edit_team_registry(
            hackathon_team.hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        await self._validate_hackathon_limits(
            hackathon_team.hackathon_id,
            len(await self.get_mates(to_hackathon_team_id)) + 1,
        )

        brand_mate = await self.brand_mate_service.get_mate(mate_user_id)
        if brand_mate is None:
            raise NotAMemberException()

        if brand_mate.team_id != from_brand_team_id:
            raise MateTeamMismatchException()

        hackathon_mate = await HackathonTeamMatesModel.create(
            team_id=to_hackathon_team_id,
            user_id=mate_user_id,
            is_captain=brand_mate.is_captain,
            role_desc=brand_mate.role_desc,
        )

        dto = HackathonTeamMateDto.from_tortoise(hackathon_mate)
        dto.user_name = brand_mate.user_name
        dto.user_uploads = brand_mate.user_uploads
        return dto

    async def get_captains(self, team_id: int) -> list[HackathonTeamMateDto]:
        mates = await HackathonTeamMatesModel.filter(
            team_id=team_id, is_captain=True
        )

        dtos = [HackathonTeamMateDto.from_tortoise(mate) for mate in mates]
        external_user_info = await self.user_service.try_get_user_info_many(
            dto_utils.export_int_fields(dtos, "user_id")
        )
        names = self.user_service.get_name_map(external_user_info)
        user_map = dict((user.id, user) for user in external_user_info)

        for dto in dtos:
            if dto.user_id in user_map:
                dto.user_uploads = user_map[dto.user_id].uploads

        return dto_utils.inject_mapping(
            dtos, names, "user_id", "user_name", strict=True
        )

    async def get_hackathon_teams(
        self, hackathon_id: int
    ) -> list[HackathonTeamDto]:
        teams = await HackathonTeamModel.filter(hackathon_id=hackathon_id)
        hackathon_data = await self.hackathon_service.try_get_hackathon_data(
            hackathon_id
        )
        hackathon_name = hackathon_data.name if hackathon_data else None

        return [
            HackathonTeamDto.from_tortoise(
                team,
                hackathon_name,
                await self.submission_service.get_submission(
                    team.hackathon_id, team.id
                ),
            )
            for team in teams
        ]

    async def get_hackathon_teams_many(
        self, hackathon_team_ids: list[int]
    ) -> list[HackathonTeamDto]:
        teams = await HackathonTeamModel.filter(id__in=hackathon_team_ids)
        return [
            HackathonTeamDto.from_tortoise(
                team,
                None,
                await self.submission_service.get_submission(
                    team.hackathon_id, team.id
                ),
            )
            for team in teams
        ]

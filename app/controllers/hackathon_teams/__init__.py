from app.controllers.mate import IMateController, get_mate_controller
from app.controllers.team import ITeamController, get_team_controller
from app.controllers.team.exceptions import TeamDoesNotExistException
from app.controllers.mate.exceptions import NotAMemberException
from app.controllers.mate.dto import TeamMateDto
from tortoise.transactions import in_transaction
from typing import Protocol, cast
from functools import lru_cache
from app.config import Settings
from fastapi import Depends

from app.controllers.hackathon_team_submissions import (
    IHackathonTeamSubmissionsController,
    get_hackathon_team_submissions_controller,
)

from .exceptions import (
    CantCreateTeamWithoutCaptainException,
    UserAlreadyParticipatingInHackathonException,
    ThisBrandTeamAlreadyParticipatesException,
    TeamDoesNotFitHackathonException,
    CantEditHackathonTeamsException,
    CantMakeSuchLargeTeamException,
    CantCreateEmptyTeamException,
    MateTeamMismatchException,
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

from app.controllers.hackathon import (
    get_hackathon_controller,
    IHackathonController,
)


class IHackathonTeamsController(Protocol):
    hackathon_controller: IHackathonController
    brand_mate_controller: IMateController
    brand_team_controller: ITeamController
    submission_controller: IHackathonTeamSubmissionsController

    async def get_registered_users_count(self, hackathon_id: int) -> int: ...
    async def get_mates(self, team_id: int) -> list[HackathonTeamMateDto]: ...
    async def mate_exists(self, user_id: int, hackathon_id: int) -> bool: ...
    async def get_mate(
        self, user_id: int, hackathon_id: int
    ) -> HackathonTeamMateDto: ...
    async def get_by_id(self, team_id: int) -> HackathonTeamDto: ...
    async def get_total(self, team_id: int) -> HackathonTeamWithMatesDto: ...
    async def get_team_by_name_exists(
        self, name: str, hackathon_id: int
    ) -> bool: ...
    async def create(
        self, brand_team_id: int, hackathon_id: int, mate_user_ids: list[int]
    ) -> HackathonTeamWithMatesDto: ...
    async def set_mate_is_captain(
        self, hackathon_id: int, mate_user_id: int, is_captain: bool
    ) -> HackathonTeamMateDto: ...
    async def set_mate_role_desc(
        self, hackathon_id: int, mate_user_id: int, role_desc: str
    ) -> HackathonTeamMateDto: ...
    async def delete_team(self, team_id: int) -> HackathonTeamDto: ...
    async def remove_mate(
        self, hackathon_id: int, mate_user_id: int
    ) -> HackathonTeamMateDto: ...
    async def add_mate(
        self,
        from_brand_team_id: int,
        to_hackathon_team_id: int,
        mate_user_id: int,
    ) -> HackathonTeamMateDto: ...
    async def get_captains(
        self, team_id: int
    ) -> list[HackathonTeamMateDto]: ...
    async def get_hackathon_teams(
        self, hackathon_id: int
    ) -> list[HackathonTeamDto]: ...


class HackathonTeamsController(IHackathonTeamsController):
    def __init__(
        self,
        hackathon_controller: IHackathonController,
        brand_mate_controller: IMateController,
        brand_team_controller: ITeamController,
        submission_controller: IHackathonTeamSubmissionsController,
    ):
        self.hackathon_controller = hackathon_controller
        self.brand_mate_controller = brand_mate_controller
        self.brand_team_controller = brand_team_controller
        self.submission_controller = submission_controller

    async def get_registered_users_count(self, hackathon_id: int) -> int:
        return await HackathonTeamMatesModel.filter(
            team__hackathon_id=hackathon_id
        ).count()

    async def get_mates(self, team_id: int) -> list[HackathonTeamMateDto]:
        mates = await HackathonTeamMatesModel.filter(team_id=team_id)

        return [HackathonTeamMateDto.from_tortoise(mate) for mate in mates]

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
        return HackathonTeamMateDto.from_tortoise(
            await self._get_mate(user_id, hackathon_id)
        )

    async def _get_by_id(self, team_id: int) -> HackathonTeamModel:
        team = await HackathonTeamModel.get_or_none(id=team_id)
        if team is None:
            raise TeamDoesNotExistException()

        return team

    async def _get_submission_url(
        self,
        hackathon_id: int,
        team_id: int,
    ) -> str | None:
        submission = await self.submission_controller.get_submission(
            hackathon_id, team_id
        )

        if submission:
            return self.submission_controller.generate_redirect_link(
                Settings.PUBLIC_API_URL,
                hackathon_id,
                team_id,
            )

        return None

    async def get_by_id(self, team_id: int) -> HackathonTeamDto:
        team = await self._get_by_id(team_id)
        return HackathonTeamDto.from_tortoise(
            team,
            submission_url=await self._get_submission_url(
                team.hackathon_id, team.id
            ),
        )

    async def get_total(self, team_id: int) -> HackathonTeamWithMatesDto:
        team = await self._get_by_id(team_id)
        mates = await self.get_mates(team_id)

        return HackathonTeamWithMatesDto(
            id=team.id,
            hackathon_id=team.hackathon_id,
            name=team.name,
            mates=mates,
            submission_url=await self._get_submission_url(
                team.hackathon_id, team.id
            ),
        )

    async def _validate_hackathon_limits(
        self, hackathon_id: int, mates_count: int
    ):
        hackathon = await self.hackathon_controller.get_hackathon_data(
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

        if not await self.hackathon_controller.can_edit_team_registry(
            hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        brand_team = await self.brand_team_controller.get_info(brand_team_id)

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
                name=hackathon_team.name,
                mates=await self.get_mates(hackathon_team.id),
            )

    async def set_mate_is_captain(
        self, hackathon_id: int, mate_user_id: int, is_captain: bool
    ) -> HackathonTeamMateDto:
        mate = await self._get_mate(mate_user_id, hackathon_id)

        if not await self.hackathon_controller.can_edit_team_registry(
            (await mate.team).hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        mate.is_captain = is_captain
        await mate.save()

        return HackathonTeamMateDto.from_tortoise(mate)

    async def set_mate_role_desc(
        self, hackathon_id: int, mate_user_id: int, role_desc: str
    ) -> HackathonTeamMateDto:
        mate = await self._get_mate(mate_user_id, hackathon_id)

        if not await self.hackathon_controller.can_edit_team_registry(
            (await mate.team).hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        mate.role_desc = role_desc
        await mate.save()

        return HackathonTeamMateDto.from_tortoise(mate)

    async def delete_team(self, team_id: int) -> HackathonTeamDto:
        team = await self._get_by_id(team_id)
        await team.delete()
        return HackathonTeamDto.from_tortoise(team)

    async def remove_mate(
        self, hackathon_id: int, mate_user_id: int
    ) -> HackathonTeamMateDto:
        mate = await self._get_mate(mate_user_id, hackathon_id)

        if not await self.hackathon_controller.can_edit_team_registry(
            (await mate.team).hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        team_id = cast(int, mate.team_id)  # type: ignore[attr-defined]

        total_mates = await self.get_mates(team_id)
        if len(total_mates) == 1:
            await self.delete_team(team_id)
        else:
            await mate.delete()

        return HackathonTeamMateDto.from_tortoise(mate)

    async def add_mate(
        self,
        from_brand_team_id: int,
        to_hackathon_team_id: int,
        mate_user_id: int,
    ) -> HackathonTeamMateDto:
        hackathon_team = await self.get_by_id(to_hackathon_team_id)
        if not await self.hackathon_controller.can_edit_team_registry(
            hackathon_team.hackathon_id
        ):
            raise CantEditHackathonTeamsException()

        await self._validate_hackathon_limits(
            hackathon_team.hackathon_id,
            len(await self.get_mates(to_hackathon_team_id)) + 1,
        )

        brand_mate = await self.brand_mate_controller.get_mate(mate_user_id)
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

        return HackathonTeamMateDto.from_tortoise(hackathon_mate)

    async def get_captains(self, team_id: int) -> list[HackathonTeamMateDto]:
        captains = await HackathonTeamMatesModel.filter(
            team_id=team_id, is_captain=True
        )
        return [
            HackathonTeamMateDto.from_tortoise(captain) for captain in captains
        ]

    async def get_hackathon_teams(
        self, hackathon_id: int
    ) -> list[HackathonTeamDto]:
        teams = await HackathonTeamModel.filter(hackathon_id=hackathon_id)
        return [
            HackathonTeamDto.from_tortoise(
                team, await self._get_submission_url(hackathon_id, team.id)
            )
            for team in teams
        ]


@lru_cache
def get_hackathon_teams_controller(
    hackathon_controller: IHackathonController = Depends(
        get_hackathon_controller
    ),
    brand_mate_controller: IMateController = Depends(get_mate_controller),
    brand_team_controller: ITeamController = Depends(get_team_controller),
    submission_controller: IHackathonTeamSubmissionsController = Depends(
        get_hackathon_team_submissions_controller
    ),
) -> HackathonTeamsController:
    return HackathonTeamsController(
        hackathon_controller=hackathon_controller,
        brand_mate_controller=brand_mate_controller,
        brand_team_controller=brand_team_controller,
        submission_controller=submission_controller,
    )

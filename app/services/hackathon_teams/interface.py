from app.ports.hackathonservice import IHackathonServicePort
from app.services.brand_team.interface import ITeamService
from app.ports.event_publisher import IEventPublisherPort
from app.services.mate.interface import IMateService
from typing import Protocol

from .dto import (
    HackathonTeamWithMatesDto,
    HackathonTeamMateDto,
    HackathonTeamDto,
)

from app.services.hackathon_team_submissions.interface import (
    IHackathonTeamSubmissionsService,
)


class IHackathonTeamsService(Protocol):
    hackathon_service: IHackathonServicePort
    brand_mate_service: IMateService
    brand_team_service: ITeamService
    submission_service: IHackathonTeamSubmissionsService
    event_publisher: IEventPublisherPort

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
        self, hackathon_id: int, mate_user_id: int, silent: bool = False
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
    async def get_hackathon_teams_many(
        self, hackathon_team_ids: list[int]
    ) -> list[HackathonTeamDto]: ...

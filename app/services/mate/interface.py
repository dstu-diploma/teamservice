from app.ports.userservice import IUserServicePort
from app.services.mate.dto import TeamMateDto
from typing import Protocol


class IMateService(Protocol):
    user_service: IUserServicePort

    async def get_mate(self, user_id: int) -> TeamMateDto | None: ...
    async def get_mates(self, team_id: int) -> list[TeamMateDto]: ...
    async def get_mate_count(self, team_id: int) -> int: ...
    async def add(
        self,
        team_id: int,
        user_id: int,
        is_captain: bool,
    ) -> TeamMateDto: ...
    async def remove(
        self, user_id: int, silent: bool = False
    ) -> TeamMateDto: ...
    async def set_is_captain(
        self, user_id: int, is_captain: bool
    ) -> TeamMateDto: ...
    async def set_role_desc(
        self, user_id: int, role_desc: str
    ) -> TeamMateDto: ...
    async def get_captains(self, team_id: int) -> list[TeamMateDto]: ...

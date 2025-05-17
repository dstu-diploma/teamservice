from .dto import HackathonDto
from typing import Protocol


class IHackathonServicePort(Protocol):
    async def get_hackathon_data(self, hackathon_id: int) -> HackathonDto: ...
    async def can_edit_team_registry(self, hackathon_id: int) -> bool: ...
    async def can_upload_submissions(self, hackathon_id: int) -> bool: ...

    async def try_get_hackathon_data(
        self, hackathon_id: int
    ) -> HackathonDto | None:
        try:
            return await self.get_hackathon_data(hackathon_id)
        except Exception as e:
            return None

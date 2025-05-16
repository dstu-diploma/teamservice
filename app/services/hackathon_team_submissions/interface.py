from app.ports.hackathonservice import IHackathonServicePort
from app.ports.storage import IStoragePort
from typing import Protocol
import io

from app.services.hackathon_team_submissions.dto import (
    HackathonTeamSubmissionDto,
)


class IHackathonTeamSubmissionsService(Protocol):
    hackathon_service: IHackathonServicePort
    storage: IStoragePort

    async def get_submission(
        self, hackathon_id: int, team_id: int
    ) -> HackathonTeamSubmissionDto | None: ...
    async def upload_team_submission(
        self, hackathon_id: int, filename: str, team_id: int, file: io.BytesIO
    ) -> HackathonTeamSubmissionDto: ...
    def generate_redirect_link(
        self,
        base_url: str,
        hackathon_id: int,
        team_id: int,
    ) -> str: ...

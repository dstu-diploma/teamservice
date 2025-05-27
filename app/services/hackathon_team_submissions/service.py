from app.models.hackathon_team import HackathonTeamSubmissionModel
from app.ports.hackathonservice import IHackathonServicePort
from app.ports.storage import IStoragePort
from app.config import Settings
from . import utils
import urllib.parse
import io

from .dto import (
    HackathonTeamSubmissionDto,
)

from .exceptions import (
    HackathonTeamCantUploadSubmissionsException,
    HackathonFileTypeRestrictedException,
)

from app.services.hackathon_team_submissions.interface import (
    IHackathonTeamSubmissionsService,
)


class HackathonTeamSubmissionsService(IHackathonTeamSubmissionsService):
    def __init__(
        self,
        hackathon_service: IHackathonServicePort,
        storage: IStoragePort,
    ):
        self.hackathon_service = hackathon_service
        self.storage = storage

    async def get_submission(
        self, hackathon_id: int, team_id: int
    ) -> HackathonTeamSubmissionDto | None:
        submission = await HackathonTeamSubmissionModel.get_or_none(
            hackathon_id=hackathon_id, team_id=team_id
        )

        if submission:
            return HackathonTeamSubmissionDto.from_tortoise(
                submission,
                self.generate_redirect_link(
                    Settings.PUBLIC_API_URL, hackathon_id, team_id
                ),
            )

        return None

    async def upload_team_submission(
        self, hackathon_id: int, filename: str, team_id: int, file: io.BytesIO
    ) -> HackathonTeamSubmissionDto:
        if not await self.hackathon_service.can_upload_submissions(
            hackathon_id
        ):
            raise HackathonTeamCantUploadSubmissionsException()

        if not utils.is_allowed_file(filename, file):
            raise HackathonFileTypeRestrictedException()

        s3_key = f"team_submissions/{hackathon_id}/{team_id}/{filename}"
        content_type = utils.guess_content_type(filename)

        file.seek(0)
        self.storage.upload_file(file, "hackathons", s3_key, content_type)

        submission, _ = await HackathonTeamSubmissionModel.update_or_create(
            defaults={
                "name": filename,
                "s3_key": s3_key,
                "content_type": content_type,
            },
            team_id=team_id,
            hackathon_id=hackathon_id,
        )

        return HackathonTeamSubmissionDto.from_tortoise(
            submission,
            self.generate_redirect_link(
                Settings.PUBLIC_API_URL, hackathon_id, team_id
            ),
        )

    def generate_redirect_link(
        self,
        base_url: str,
        hackathon_id: int,
        team_id: int,
    ) -> str:
        return urllib.parse.urljoin(
            base_url, f"download/submission/{hackathon_id}/{team_id}"
        )

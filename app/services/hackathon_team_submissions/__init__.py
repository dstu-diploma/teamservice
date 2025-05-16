from app.models.hackathon_team import HackathonTeamSubmissionModel
from app.services.s3 import IS3Service, get_s3_service
from functools import lru_cache
from typing import Protocol
from fastapi import Depends
from . import utils
import io

from .dto import (
    HackathonTeamSubmissionDto,
)
from .exceptions import (
    HackathonTeamCantUploadSubmissionsException,
    HackathonFileTypeRestrictedException,
)

from app.services.hackathon import (
    IHackathonService,
    get_hackathon_service,
)


class IHackathonTeamSubmissionsService(Protocol):
    hackathon_service: IHackathonService
    s3_service: IS3Service

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


class HackathonTeamSubmissionsService(IHackathonTeamSubmissionsService):
    def __init__(
        self,
        hackathon_service: IHackathonService,
        s3_service: IS3Service,
    ):
        self.hackathon_service = hackathon_service
        self.s3_service = s3_service

    async def get_submission(
        self, hackathon_id: int, team_id: int
    ) -> HackathonTeamSubmissionDto | None:
        submission = await HackathonTeamSubmissionModel.get_or_none(
            hackathon_id=hackathon_id, team_id=team_id
        )

        if submission:
            return HackathonTeamSubmissionDto.from_tortoise(submission)

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
        self.s3_service.upload_file(file, "hackathons", s3_key, content_type)

        submission, _ = await HackathonTeamSubmissionModel.update_or_create(
            defaults={
                "name": filename,
                "s3_key": s3_key,
                "content_type": content_type,
            },
            team_id=team_id,
            hackathon_id=hackathon_id,
        )

        return HackathonTeamSubmissionDto.from_tortoise(submission)

    def generate_redirect_link(
        self,
        base_url: str,
        hackathon_id: int,
        team_id: int,
    ) -> str:
        redirect_url = (
            f"{base_url}/download/submission/{hackathon_id}/{team_id}"
        )
        return redirect_url


@lru_cache
def get_hackathon_team_submissions_service(
    hackathon_service: IHackathonService = Depends(get_hackathon_service),
    s3_service: IS3Service = Depends(get_s3_service),
) -> HackathonTeamSubmissionsService:
    return HackathonTeamSubmissionsService(hackathon_service, s3_service)

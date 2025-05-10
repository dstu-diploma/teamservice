from app.models.hackathon_team import HackathonTeamSubmissionModel
from app.controllers.s3 import IS3Controller, get_s3_controller
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

from app.controllers.hackathon import (
    IHackathonController,
    get_hackathon_controller,
)


class IHackathonTeamSubmissionsController(Protocol):
    hackathon_controller: IHackathonController
    s3_controller: IS3Controller

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


class HackathonTeamSubmissionsController(IHackathonTeamSubmissionsController):
    def __init__(
        self,
        hackathon_controller: IHackathonController,
        s3_controller: IS3Controller,
    ):
        self.hackathon_controller = hackathon_controller
        self.s3_controller = s3_controller

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
        if not await self.hackathon_controller.can_upload_submissions(
            hackathon_id
        ):
            raise HackathonTeamCantUploadSubmissionsException()

        if utils.is_allowed_file(filename, file):
            raise HackathonFileTypeRestrictedException()

        s3_key = f"team_submissions/{hackathon_id}/{team_id}/{filename}"
        content_type = utils.guess_content_type(filename)

        self.s3_controller.upload_file(file, "hackathons", s3_key, content_type)

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
            f"{base_url}/download/hackathon/{hackathon_id}/teams/{team_id}"
        )
        return redirect_url


@lru_cache
def get_hackathon_team_submissions_controller(
    hackathon_controller: IHackathonController = Depends(
        get_hackathon_controller
    ),
    s3_controller: IS3Controller = Depends(get_s3_controller),
) -> HackathonTeamSubmissionsController:
    return HackathonTeamSubmissionsController(
        hackathon_controller, s3_controller
    )

from app.dependencies import get_hackathon_team_submissions_service, get_storage
from fastapi.responses import StreamingResponse
from app.ports.storage import IStoragePort
from fastapi import APIRouter, Depends
from urllib.parse import quote

from app.services.hackathon_team_submissions.exceptions import (
    HackathonTeamCantUploadSubmissionsException,
)

from app.services.hackathon_team_submissions.interface import (
    IHackathonTeamSubmissionsService,
)

router = APIRouter(prefix="/download", include_in_schema=False)


@router.get("/submission/{hackathon_id}/{team_id}")
async def download_team_submission(
    hackathon_id: int,
    team_id: int,
    submission_service: IHackathonTeamSubmissionsService = Depends(
        get_hackathon_team_submissions_service
    ),
    s3_service: IStoragePort = Depends(get_storage),
):
    submission = await submission_service.get_submission(hackathon_id, team_id)

    if submission is None:
        raise HackathonTeamCantUploadSubmissionsException()

    s3_obj = s3_service.get_object("hackathons", submission.s3_key)

    return StreamingResponse(
        s3_obj["Body"],
        media_type=s3_obj["ContentType"],
        headers={
            "Content-Disposition": f'attachment; filename="{quote(submission.name)}"'
        },
    )

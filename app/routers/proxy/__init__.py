from app.services.s3 import IS3Service, get_s3_service
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends
from urllib.parse import quote

from app.services.hackathon_team_submissions import (
    IHackathonTeamSubmissionsService,
    get_hackathon_team_submissions_service,
)
from app.services.hackathon_team_submissions.exceptions import (
    HackathonTeamCantUploadSubmissionsException,
)


router = APIRouter(prefix="/download", include_in_schema=False)


@router.get("/submission/{hackathon_id}/{team_id}")
async def download_team_submission(
    hackathon_id: int,
    team_id: int,
    submission_service: IHackathonTeamSubmissionsService = Depends(
        get_hackathon_team_submissions_service
    ),
    s3_service: IS3Service = Depends(get_s3_service),
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

from app.controllers.s3 import IS3Controller, get_s3_controller
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends
from urllib.parse import quote

from app.controllers.hackathon_team_submissions import (
    IHackathonTeamSubmissionsController,
    get_hackathon_team_submissions_controller,
)
from app.controllers.hackathon_team_submissions.exceptions import (
    HackathonTeamCantUploadSubmissionsException,
)


router = APIRouter(prefix="/download", include_in_schema=False)


@router.get("/submission/{hackathon_id}/{team_id}")
async def download_team_submission(
    hackathon_id: int,
    team_id: int,
    submission_controller: IHackathonTeamSubmissionsController = Depends(
        get_hackathon_team_submissions_controller
    ),
    s3_controller: IS3Controller = Depends(get_s3_controller),
):
    submission = await submission_controller.get_submission(
        hackathon_id, team_id
    )

    if submission is None:
        raise HackathonTeamCantUploadSubmissionsException()

    s3_obj = s3_controller.get_object("hackathons", submission.s3_key)

    return StreamingResponse(
        s3_obj["Body"],
        media_type=s3_obj["ContentType"],
        headers={
            "Content-Disposition": f'attachment; filename="{quote(submission.name)}"'
        },
    )

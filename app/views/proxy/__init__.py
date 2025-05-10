@router.get("/submission/{hackathon_id}/{team_id}")
async def download_team_submission(
    hackathon_id: int,
    team_id: int,
    hackathon_teams_controller: HackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
    s3_controller: IS3Controller = Depends(get_s3_controller),
):
    submission = await hackathon_teams_controller.get_submission(
        hackathon_id, team_id
    )

    if submission is None:
        raise HackathonTeamNoSubmissionException()

    s3_obj = s3_controller.get_object("hackathons", submission.s3_key)

    return StreamingResponse(
        s3_obj["Body"],
        media_type=s3_obj["ContentType"],
        headers={
            "Content-Disposition": f'attachment; filename="{submission.name}"'
        },
    )

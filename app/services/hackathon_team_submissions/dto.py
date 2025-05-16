from app.models.hackathon_team import HackathonTeamSubmissionModel
from datetime import datetime
from pydantic import BaseModel


class HackathonTeamSubmissionDto(BaseModel):
    id: int
    team_id: int
    hackathon_id: int
    name: str
    s3_key: str
    content_type: str
    uploaded_at: datetime

    @staticmethod
    def from_tortoise(submission: HackathonTeamSubmissionModel):
        return HackathonTeamSubmissionDto(
            id=submission.id,
            team_id=submission.team_id,  # type: ignore[attr-defined]
            hackathon_id=submission.hackathon_id,
            name=submission.name,
            s3_key=submission.s3_key,
            content_type=submission.content_type,
            uploaded_at=submission.uploaded_at,
        )

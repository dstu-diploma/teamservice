from pydantic import BaseModel
from datetime import datetime


class HackathonDto(BaseModel):
    id: int
    name: str
    max_participant_count: int
    max_team_mates_count: int

    start_date: datetime
    score_start_date: datetime
    end_date: datetime

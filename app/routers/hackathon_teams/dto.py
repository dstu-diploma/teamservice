from pydantic import BaseModel


class CreateHackathonTeamDto(BaseModel):
    hackathon_id: int
    mate_user_ids: list[int]

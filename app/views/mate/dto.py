from pydantic import BaseModel


class MateCaptainRightsDto(BaseModel):
    user_id: int
    is_captain: bool

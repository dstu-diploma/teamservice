from app.controllers.team import ITeamController, get_team_controller
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.auth import get_user_dto
from app.controllers.team.dto import TeamDto
from pydantic import BaseModel
from fastapi import Depends


class TeamOwnerDto(BaseModel):
    user_dto: AccessJWTPayloadDto
    team_dto: TeamDto


async def get_team_owner(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    team_controller: ITeamController = Depends(get_team_controller),
) -> TeamOwnerDto:
    team = await team_controller.get_by_captain(user_dto.user_id)
    return TeamOwnerDto(user_dto=user_dto, team_dto=team)

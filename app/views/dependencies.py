from fastapi import Depends
from pydantic import BaseModel
from app.controllers.auth import get_user_dto
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.team import TeamController, get_team_controller
from app.controllers.team.dto import TeamDto
from app.controllers.team.exceptions import UserIsNotOwnerOfGroupException


class TeamOwnerDto(BaseModel):
    user_dto: AccessJWTPayloadDto
    team_dto: TeamDto


async def get_team_owner(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: TeamController = Depends(get_team_controller),
) -> TeamOwnerDto:
    team = await controller.get_by_owner(user_dto.user_id)
    if team is None:
        raise UserIsNotOwnerOfGroupException()

    return TeamOwnerDto(user_dto=user_dto, team_dto=team)

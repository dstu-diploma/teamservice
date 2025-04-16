from fastapi import Depends
from app.controllers.auth import get_user_dto
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.team import TeamController, get_team_controller
from app.controllers.team.dto import TeamDto
from app.controllers.team.exceptions import UserIsNotOwnerOfGroupException


async def get_team_owner(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: TeamController = Depends(get_team_controller),
) -> tuple[AccessJWTPayloadDto, TeamDto]:
    team = await controller.get_by_owner(user_dto.user_id)
    if team is None:
        raise UserIsNotOwnerOfGroupException()
    return (user_dto, team)

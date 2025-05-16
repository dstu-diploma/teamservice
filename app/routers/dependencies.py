from app.services.team import ITeamService, get_team_service
from app.services.auth.dto import AccessJWTPayloadDto
from app.services.auth import PermittedAction
from app.services.team.dto import TeamDto
from app.acl.permissions import Permissions
from pydantic import BaseModel
from fastapi import Depends


class TeamOwnerDto(BaseModel):
    user_dto: AccessJWTPayloadDto
    team_dto: TeamDto


async def get_team_owner(
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.CanBeInTeam)
    ),
    team_service: ITeamService = Depends(get_team_service),
) -> TeamOwnerDto:
    team = await team_service.get_by_captain(user_dto.user_id)
    return TeamOwnerDto(user_dto=user_dto, team_dto=team)

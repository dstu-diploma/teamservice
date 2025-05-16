from app.services.team import ITeamService, get_team_service
from .auth import get_token_from_header
from fastapi import APIRouter, Depends

from app.services.hackathon_teams import (
    IHackathonTeamsService,
    get_hackathon_teams_service,
)

router = APIRouter(
    tags=["Internal"],
    prefix="/internal",
    include_in_schema=False,
)


@router.get("/{id}")
async def get_team_by_id(
    id: int,
    _=Depends(get_token_from_header),
    service: ITeamService = Depends(get_team_service),
):
    return await service.exists(id)


@router.get("/hackathon/{hackathon_id}/teams")
async def get_hackathon_teams(
    hackathon_id: int,
    _=Depends(get_token_from_header),
    service: IHackathonTeamsService = Depends(get_hackathon_teams_service),
):
    return await service.get_hackathon_teams(hackathon_id)


# на самом деле hackathon_id тут не нужен, но нужно соблюдать нейминг
@router.get("/hackathon/{hackathon_id}/teams/{team_id}")
async def get_hack_team_by_id(
    hackathon_id: int,
    team_id: int,
    _=Depends(get_token_from_header),
    service: IHackathonTeamsService = Depends(get_hackathon_teams_service),
):
    return await service.get_total(team_id)

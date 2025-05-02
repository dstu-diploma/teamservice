from app.controllers.team import ITeamController, get_team_controller
from .auth import get_token_from_header
from fastapi import APIRouter, Depends

from app.controllers.hackathon_teams import (
    IHackathonTeamsController,
    get_hackathon_teams_controller,
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
    controller: ITeamController = Depends(get_team_controller),
):
    return await controller.exists(id)


@router.get("/hackathon/{hackathon_id}/teams")
async def get_hackathon_teams(
    hackathon_id: int,
    _=Depends(get_token_from_header),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    return await controller.get_hackathon_teams(hackathon_id)


# на самом деле hackathon_id тут не нужен, но нужно соблюдать нейминг
@router.get("/hackathon/{hackathon_id}/teams/{team_id}")
async def get_hack_team_by_id(
    hackathon_id: int,
    team_id: int,
    _=Depends(get_token_from_header),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    return await controller.get_total(team_id)

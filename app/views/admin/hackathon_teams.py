from app.controllers.auth import UserWithRole
from fastapi import APIRouter, Depends

from app.controllers.hackathon_teams import (
    get_hackathon_teams_controller,
    IHackathonTeamsController,
)
from app.controllers.hackathon_teams.dto import HackathonTeamDto

router = APIRouter(
    prefix="/hackathon",
)


@router.get(
    "/{hackathon_id}",
    response_model=list[HackathonTeamDto],
    summary="Список всех команд",
)
async def get_all_teams(
    hackathon_id: int,
    _=Depends(UserWithRole("admin")),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Возвращает список всех команд для хакатона с заданным ID.
    """
    return await controller.get_hackathon_teams(hackathon_id)

from app.controllers.team import TeamController, get_team_controller
from .auth import get_token_from_header
from fastapi import APIRouter, Depends

router = APIRouter(
    tags=["Internal"],
    prefix="/internal",
    include_in_schema=False,
)


@router.get("/{id}")
async def get_team_by_id(
    id: int,
    _=Depends(get_token_from_header),
    controller: TeamController = Depends(get_team_controller),
):
    return await controller.exists(id)

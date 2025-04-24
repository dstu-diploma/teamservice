from app.controllers.mate import MateController, get_mate_controller
from app.controllers.team import TeamController, get_team_controller
from app.controllers.mate.exceptions import NotAMemberException
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.auth import get_user_dto
from fastapi import APIRouter, Depends

router = APIRouter(tags=["Основное"], prefix="/mate")


@router.get("/", summary="Возвращает список участников группы")
async def get_team_mates(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    mate_controller: MateController = Depends(get_mate_controller),
    team_controller: TeamController = Depends(get_team_controller),
):
    """
    Возвращает список участников группы. Владелец сюда не входит.
    """
    mate_dto = await mate_controller.get_mate(user_dto.user_id)
    if mate_dto:
        return await mate_controller.get_mates(mate_dto.team_id)

    team_dto = await team_controller.get_by_owner(user_dto.user_id)
    if team_dto:
        return await mate_controller.get_mates(team_dto.id)

    raise NotAMemberException()

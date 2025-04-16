from fastapi import APIRouter, Depends

from app.controllers.auth import get_user_dto
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.team import TeamController, get_team_controller
from app.controllers.team.dto import TeamDto, TeamMateDto
from app.views.root.dependencies import get_team_owner
from app.views.root.dto import TeamNameDto


router = APIRouter(tags=["Основное"], prefix="")


@router.post("/", response_model=TeamDto, summary="Создание команды")
async def create_team(
    create_dto: TeamNameDto,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: TeamController = Depends(get_team_controller),
):
    return await controller.create(create_dto.name, user_dto.user_id)


@router.get(
    "/{id}", response_model=TeamDto, summary="Получение инфоромации о команде"
)
async def get_info(
    id: int, controller: TeamController = Depends(get_team_controller)
):
    return await controller.get_info(id)


@router.get(
    "/{id}/mates",
    response_model=list[TeamMateDto],
    summary="Получение списка участников команды",
)
async def get_mates(
    id: int, controller: TeamController = Depends(get_team_controller)
):
    return await controller.get_mates(id)


@router.post(
    "/name", response_model=TeamDto, summary="Изменение названия команды"
)
async def update_name(
    update_dto: TeamNameDto,
    owner_pack: tuple[AccessJWTPayloadDto, TeamDto] = Depends(get_team_owner),
    controller: TeamController = Depends(get_team_controller),
):
    """Изменяет название команды у текущего залогиненного пользователя.
    Работает только в случае, если пользователь - владелец команды
    """
    _, team = owner_pack
    return await controller.update_name(team.id, update_dto.name)

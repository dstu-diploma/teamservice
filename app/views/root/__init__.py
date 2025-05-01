from fastapi import APIRouter, Depends

from app.controllers.auth import get_user_dto
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.team import ITeamController, get_team_controller
from app.controllers.team.dto import TeamDto, TeamWithMatesDto
from app.views.dependencies import TeamOwnerDto, get_team_owner
from app.views.root.dto import TeamNameDto


router = APIRouter(tags=["Основное"], prefix="")


@router.post("/", response_model=TeamDto, summary="Создание команды")
async def create_team(
    create_dto: TeamNameDto,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: ITeamController = Depends(get_team_controller),
):
    """
    Регистрирует новую команду.
    """
    return await controller.create(create_dto.name, user_dto.user_id)


@router.get(
    "/info/{id}",
    response_model=TeamWithMatesDto,
    summary="Получение инфоромации о команде",
)
async def get_info(
    id: int, controller: ITeamController = Depends(get_team_controller)
):
    """
    Возвращает информацию о команде. Помимо информации, сюда входит список всех участников.
    """
    return await controller.get_info(id)


@router.post(
    "/name", response_model=TeamDto, summary="Изменение названия команды"
)
async def update_name(
    update_dto: TeamNameDto,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    controller: ITeamController = Depends(get_team_controller),
):
    """
    Изменяет название команды у текущего залогиненного пользователя.
    Работает только в случае, если пользователь - владелец команды.
    """
    return await controller.update_name(owner_dto.team_dto.id, update_dto.name)

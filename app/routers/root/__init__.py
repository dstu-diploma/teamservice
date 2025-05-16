from app.controllers.team import ITeamController, get_team_controller
from app.routers.dependencies import TeamOwnerDto, get_team_owner
from app.controllers.team.dto import TeamDto, TeamWithMatesDto
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.auth import PermittedAction
from app.acl.permissions import Permissions
from app.routers.root.dto import TeamNameDto
from fastapi import APIRouter, Depends


router = APIRouter(tags=["Основное"], prefix="")


@router.post("/", response_model=TeamDto, summary="Создание команды")
async def create_team(
    create_dto: TeamNameDto,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.CreateTeam)
    ),
    controller: ITeamController = Depends(get_team_controller),
):
    """
    Регистрирует новую команду.
    """
    return await controller.create(create_dto.name, user_dto.user_id)


@router.get(
    "/info/{team_id}",
    response_model=TeamWithMatesDto,
    summary="Получение инфоромации о команде",
)
async def get_info(
    team_id: int,
    _=Depends(PermittedAction(Permissions.GetTeamInfo)),
    controller: ITeamController = Depends(get_team_controller),
):
    """
    Возвращает информацию о команде. Помимо информации, сюда входит список всех участников.
    """
    return await controller.get_info(team_id)


@router.get(
    "/info",
    response_model=TeamWithMatesDto,
    summary="Получение инфоромации о своей команде",
)
async def get_info_by_user(
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.GetTeamInfo)
    ),
    controller: ITeamController = Depends(get_team_controller),
):
    """
    Возвращает информацию о команде залогиненного пользователя. Помимо информации, сюда входит список всех участников.
    """
    return await controller.get_by_mate(user_dto.user_id)


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

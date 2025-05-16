from app.services.brand_team.dto import TeamDto, TeamWithMatesDto
from app.dependencies import get_mate_service, get_team_service
from app.services.brand_team.interface import ITeamService
from app.routers.mate.dto import MateCaptainRightsDto
from app.services.mate.interface import IMateService
from app.routers.admin.dto import ChangeNameDto
from app.services.mate.dto import TeamMateDto
from app.services.auth import PermittedAction
from app.acl.permissions import Permissions
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/brand",
)


@router.get("/", response_model=list[TeamDto], summary="Список всех команд")
async def get_all_teams(
    _=Depends(PermittedAction(Permissions.GetAllTeams)),
    team_service: ITeamService = Depends(get_team_service),
):
    """
    Возвращает список всех команд.
    """
    return await team_service.get_all()


@router.post("/name", response_model=TeamDto, summary="Изменение названия")
async def change_name(
    name_dto: ChangeNameDto,
    _=Depends(PermittedAction(Permissions.UpdateBrandTeam)),
    team_service: ITeamService = Depends(get_team_service),
):
    """
    Изменяет название команды. Название должно быть уникальным.
    """
    return await team_service.update_name(name_dto.team_id, name_dto.new_name)


@router.get(
    "/{team_id}",
    response_model=TeamWithMatesDto,
    summary="Полная информация о команде",
)
async def get_full_team_info(
    team_id: int,
    _=Depends(PermittedAction(Permissions.GetAllTeams)),
    team_service: ITeamService = Depends(get_team_service),
):
    """
    Возвращает полную информацию о команде.
    """
    return await team_service.get_info(team_id)


@router.delete("/{team_id}", summary="Удаление команды")
async def delete_team(
    team_id: int,
    _=Depends(PermittedAction(Permissions.DeleteBrandTeam)),
    team_service: ITeamService = Depends(get_team_service),
):
    """
    Удаляет команду из списка команд.
    """
    return await team_service.delete(team_id)


@router.post(
    "/captain-rights",
    response_model=TeamMateDto,
    summary="Передача прав владельца",
)
async def change_owner(
    dto: MateCaptainRightsDto,
    _=Depends(PermittedAction(Permissions.UpdateBrandTeam)),
    mate_service: IMateService = Depends(get_mate_service),
):
    """
    Устанавливает права капитана команды. Предыдущий владелец станет участником.
    """
    return await mate_service.set_is_captain(dto.user_id, dto.is_captain)

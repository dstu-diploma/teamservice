from app.controllers.mate import IMateController, get_mate_controller
from app.controllers.team import ITeamController, get_team_controller
from app.controllers.team.dto import TeamDto, TeamWithMatesDto
from app.views.mate.dto import MateCaptainRightsDto
from app.controllers.mate.dto import TeamMateDto
from app.controllers.auth import PermittedAction
from app.views.admin.dto import ChangeNameDto
from app.acl.permissions import Permissions
from fastapi import APIRouter, Depends


router = APIRouter(
    prefix="/brand",
)


@router.get("/", response_model=list[TeamDto], summary="Список всех команд")
async def get_all_teams(
    _=Depends(PermittedAction(Permissions.GetAllTeams)),
    team_controller: ITeamController = Depends(get_team_controller),
):
    """
    Возвращает список всех команд.
    """
    return await team_controller.get_all()


@router.post("/name", response_model=TeamDto, summary="Изменение названия")
async def change_name(
    name_dto: ChangeNameDto,
    _=Depends(PermittedAction(Permissions.UpdateBrandTeam)),
    team_controller: ITeamController = Depends(get_team_controller),
):
    """
    Изменяет название команды. Название должно быть уникальным.
    """
    return await team_controller.update_name(
        name_dto.team_id, name_dto.new_name
    )


@router.get(
    "/{team_id}",
    response_model=TeamWithMatesDto,
    summary="Полная информация о команде",
)
async def get_full_team_info(
    team_id: int,
    _=Depends(PermittedAction(Permissions.GetAllTeams)),
    team_controller: ITeamController = Depends(get_team_controller),
):
    """
    Возвращает полную информацию о команде.
    """
    return await team_controller.get_info(team_id)


@router.delete("/{team_id}", summary="Удаление команды")
async def delete_team(
    team_id: int,
    _=Depends(PermittedAction(Permissions.DeleteBrandTeam)),
    team_controller: ITeamController = Depends(get_team_controller),
):
    """
    Удаляет команду из списка команд.
    """
    return await team_controller.delete(team_id)


@router.post(
    "/captain-rights",
    response_model=TeamMateDto,
    summary="Передача прав владельца",
)
async def change_owner(
    dto: MateCaptainRightsDto,
    _=Depends(PermittedAction(Permissions.UpdateBrandTeam)),
    mate_controller: IMateController = Depends(get_mate_controller),
):
    """
    Устанавливает права капитана команды. Предыдущий владелец станет участником.
    """
    return await mate_controller.set_is_captain(dto.user_id, dto.is_captain)

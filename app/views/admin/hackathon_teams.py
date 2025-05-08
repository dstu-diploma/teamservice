from app.controllers.team import ITeamController, get_team_controller
from .dto import AdminAddMateDto, AdminMateCaptainRightsDto
from app.controllers.auth import PermittedAction
from app.views.mate.dto import MateRoleDescDto
from app.acl.permissions import Permissions
from fastapi import APIRouter, Depends

from app.controllers.hackathon_teams import (
    get_hackathon_teams_controller,
    IHackathonTeamsController,
)
from app.controllers.hackathon_teams.dto import (
    HackathonTeamWithMatesDto,
    HackathonTeamMateDto,
    HackathonTeamDto,
)


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
    _=Depends(PermittedAction(Permissions.GetAllTeams)),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Возвращает список всех команд для хакатона с заданным ID.
    """
    return await controller.get_hackathon_teams(hackathon_id)


@router.get(
    "/{hackathon_id}/team/{team_id}",
    response_model=HackathonTeamWithMatesDto,
    summary="Информация о команде",
)
async def get_team_info(
    hackathon_id: int,
    team_id: int,
    _=Depends(PermittedAction(Permissions.GetAllTeams)),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Возвращает полную информацию о хакатоновской команде с заданным ID.
    """
    return await controller.get_total(team_id)


@router.delete(
    "/{hackathon_id}/team/{team_id}",
    response_model=HackathonTeamDto,
    summary="Удаление команды",
)
async def delete_team(
    hackathon_id: int,
    team_id: int,
    _=Depends(PermittedAction(Permissions.DeleteHackathonTeam)),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Удаляет команду с заданным ID.
    """
    return await controller.delete_team(team_id)


@router.put(
    "/{hackathon_id}/mate/{mate_user_id}/role-desc",
    response_model=HackathonTeamWithMatesDto,
    summary="Установить название роли",
)
async def set_role_desc(
    hackathon_id: int,
    mate_user_id: int,
    dto: MateRoleDescDto,
    _=Depends(PermittedAction(Permissions.UpdateHackathonTeam)),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Устанавливает пользователю описание роли (например: Backend/Frontend; Python, Lua).
    Пользователь должен быть в команде.
    """
    return await controller.set_mate_role_desc(
        hackathon_id, mate_user_id, dto.role_desc
    )


@router.put(
    "/{hackathon_id}/mate/{mate_user_id}/captain-rights",
    response_model=HackathonTeamMateDto,
    summary="Изменение прав капитанства",
)
async def set_mate_is_captain(
    hackathon_id: int,
    mate_user_id: int,
    dto: AdminMateCaptainRightsDto,
    _=Depends(PermittedAction(Permissions.UpdateHackathonTeam)),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Устанавливает права капитана пользователю.
    """
    return await controller.set_mate_is_captain(
        hackathon_id, mate_user_id, dto.is_captain
    )


@router.delete(
    "/{hackathon_id}/mate/{mate_user_id}",
    response_model=HackathonTeamMateDto,
    summary="Удаление участника",
)
async def leave_team(
    hackathon_id: int,
    mate_user_id: int,
    _=Depends(PermittedAction(Permissions.UpdateHackathonTeam)),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Удаляет пользователя из команды.
    Если в команде больше не останется участников, то она будет удалена.
    """
    return await controller.remove_mate(hackathon_id, mate_user_id)


@router.post(
    "/{hackathon_id}/mate/{mate_user_id}/",
    response_model=HackathonTeamMateDto,
    summary="Добавление участника",
)
async def add_mate(
    hackathon_id: int,
    mate_user_id: int,
    dto: AdminAddMateDto,
    _=Depends(PermittedAction(Permissions.UpdateHackathonTeam)),
    brand_team_controller: ITeamController = Depends(get_team_controller),
    hack_team_controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Добавляет участника хакатоновской команды. Права капитанства наследуются автоматически.
    """
    brand_team = await brand_team_controller.get_by_mate(mate_user_id)
    return await hack_team_controller.add_mate(
        brand_team.id, dto.team_id, mate_user_id
    )

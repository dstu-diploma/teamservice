from app.services.team import ITeamService, get_team_service
from .dto import AdminAddMateDto, AdminMateCaptainRightsDto
from app.services.auth import PermittedAction
from app.routers.mate.dto import MateRoleDescDto
from app.acl.permissions import Permissions
from fastapi import APIRouter, Depends

from app.services.hackathon_teams import (
    get_hackathon_teams_service,
    IHackathonTeamsService,
)
from app.services.hackathon_teams.dto import (
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
    service: IHackathonTeamsService = Depends(get_hackathon_teams_service),
):
    """
    Возвращает список всех команд для хакатона с заданным ID.
    """
    return await service.get_hackathon_teams(hackathon_id)


@router.get(
    "/{hackathon_id}/team/{team_id}",
    response_model=HackathonTeamWithMatesDto,
    summary="Информация о команде",
)
async def get_team_info(
    hackathon_id: int,
    team_id: int,
    _=Depends(PermittedAction(Permissions.GetAllTeams)),
    service: IHackathonTeamsService = Depends(get_hackathon_teams_service),
):
    """
    Возвращает полную информацию о хакатоновской команде с заданным ID.
    """
    return await service.get_total(team_id)


@router.delete(
    "/{hackathon_id}/team/{team_id}",
    response_model=HackathonTeamDto,
    summary="Удаление команды",
)
async def delete_team(
    hackathon_id: int,
    team_id: int,
    _=Depends(PermittedAction(Permissions.DeleteHackathonTeam)),
    service: IHackathonTeamsService = Depends(get_hackathon_teams_service),
):
    """
    Удаляет команду с заданным ID.
    """
    return await service.delete_team(team_id)


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
    service: IHackathonTeamsService = Depends(get_hackathon_teams_service),
):
    """
    Устанавливает пользователю описание роли (например: Backend/Frontend; Python, Lua).
    Пользователь должен быть в команде.
    """
    return await service.set_mate_role_desc(
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
    service: IHackathonTeamsService = Depends(get_hackathon_teams_service),
):
    """
    Устанавливает права капитана пользователю.
    """
    return await service.set_mate_is_captain(
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
    service: IHackathonTeamsService = Depends(get_hackathon_teams_service),
):
    """
    Удаляет пользователя из команды.
    Если в команде больше не останется участников, то она будет удалена.
    """
    return await service.remove_mate(hackathon_id, mate_user_id)


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
    brand_team_service: ITeamService = Depends(get_team_service),
    hack_team_service: IHackathonTeamsService = Depends(
        get_hackathon_teams_service
    ),
):
    """
    Добавляет участника хакатоновской команды. Права капитанства наследуются автоматически.
    """
    brand_team = await brand_team_service.get_by_mate(mate_user_id)
    return await hack_team_service.add_mate(
        brand_team.id, dto.team_id, mate_user_id
    )

from app.services.mate import IMateService, get_mate_service
from app.services.team import ITeamService, get_team_service
from app.routers.mate.dto import MateCaptainRightsDto, MateRoleDescDto
from app.services.mate.exceptions import NotAMemberException
from app.routers.dependencies import TeamOwnerDto, get_team_owner
from app.services.auth.dto import AccessJWTPayloadDto
from app.services.mate.dto import TeamMateDto
from app.services.auth import PermittedAction
from app.acl.permissions import Permissions
from fastapi import APIRouter, Depends

from app.routers.mate.exceptions import (
    NoMoreCaptainsException,
    NotYourMateException,
)


router = APIRouter(tags=["Основное"], prefix="/mate")


@router.get(
    "/", response_model=list[TeamMateDto], summary="Список участников группы"
)
async def get_team_mates(
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.GetTeamInfo)
    ),
    mate_service: IMateService = Depends(get_mate_service),
):
    """
    Возвращает список участников группы.
    """
    mate_dto = await mate_service.get_mate(user_dto.user_id)
    if mate_dto:
        return await mate_service.get_mates(mate_dto.team_id)

    raise NotAMemberException()


async def _delete_mate(
    user_id: int,
    mate_service: IMateService,
    team_service: ITeamService,
    team_id: int | None = None,
) -> TeamMateDto:
    mate = await mate_service.get_mate(user_id)

    if mate is None:
        raise NotAMemberException()

    if team_id is None:
        team_id = mate.team_id

    if mate.team_id != team_id:
        raise NotYourMateException()

    await mate_service.remove(user_id)
    if await mate_service.get_mate_count(team_id) == 0:
        await team_service.delete(team_id)

    return mate


@router.delete(
    "/",
    response_model=TeamMateDto,
    summary="Выход из команды",
)
async def leave_team(
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateSelf)
    ),
    mate_service: IMateService = Depends(get_mate_service),
    team_service: ITeamService = Depends(get_team_service),
):
    """
    Удаляет текущего пользователя из команды-бренда.
    Если в команде больше не останется участников, то она будет удалена.
    """
    return await _delete_mate(user_dto.user_id, mate_service, team_service)


@router.delete(
    "/{user_id}",
    response_model=TeamMateDto,
    summary="Исключение участника",
)
async def delete_mate(
    user_id: int,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    mate_service: IMateService = Depends(get_mate_service),
    team_service: ITeamService = Depends(get_team_service),
):
    """
    Удаляет участника команды-бренда. Текущий пользователь должен быть капитаном.
    Если в команде больше не останется участников, то она будет удалена.
    """
    return await _delete_mate(
        user_id, mate_service, team_service, owner_dto.team_dto.id
    )


@router.put(
    "/role-desc",
    response_model=TeamMateDto,
    summary="Установить себе описание роли",
)
async def set_role_desc(
    dto: MateRoleDescDto,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateSelf)
    ),
    mate_service: IMateService = Depends(get_mate_service),
):
    """
    Устанавливает текущему пользователю описание роли (например: Backend/Frontend; Python, Lua).
    Текущий пользователь должен быть в команде.
    """
    mate_dto = await mate_service.get_mate(user_dto.user_id)
    if mate_dto:
        return await mate_service.set_role_desc(user_dto.user_id, dto.role_desc)

    raise NotAMemberException()


@router.put(
    "/captain-rights",
    response_model=TeamMateDto,
    summary="Установка прав капитана",
)
async def set_captain_rights(
    dto: MateCaptainRightsDto,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    mate_service: IMateService = Depends(get_mate_service),
):
    """
    Устанавливает права капитана пользователю.
    Текущий пользователь сам должен являться капитаном.
    Если попытаться снять права капитана с единственного участника, то вернет 400.
    """
    if (
        not dto.is_captain
        and len(await mate_service.get_captains(owner_dto.team_dto.id)) <= 1
    ):
        raise NoMoreCaptainsException()

    return await mate_service.set_is_captain(dto.user_id, dto.is_captain)

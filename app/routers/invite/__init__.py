from app.routers.dependencies import TeamOwnerDto, get_team_owner
from app.services.auth.dto import AccessJWTPayloadDto
from app.services.invite.dto import TeamInviteDto
from app.dependencies import get_invite_service
from app.services.auth import PermittedAction
from app.acl.permissions import Permissions
from fastapi import APIRouter, Depends

from app.services.invite.service import InviteService


router = APIRouter(tags=["Основное"], prefix="/invite")


@router.get(
    "/",
    response_model=list[TeamInviteDto],
    summary="Получение списка приглашений",
)
async def get_user_invites(
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateSelf)
    ),
    service: InviteService = Depends(get_invite_service),
):
    """
    Возвращает список всех приглашений в команды для текущего пользователя.
    """
    return await service.get_user_invites(user_dto.user_id)


@router.post(
    "/create/{user_id}",
    response_model=TeamInviteDto,
    summary="Приглашение пользователя",
)
async def invite_user(
    user_id: int,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    service: InviteService = Depends(get_invite_service),
):
    """
    Отправляет пользователю приглашение в команду.
    """
    return await service.invite_user(owner_dto.team_dto.id, user_id)


@router.post("/{team_id}", summary="Принятие приглашения")
async def accept_invite(
    team_id: int,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.AcceptInvite)
    ),
    service: InviteService = Depends(get_invite_service),
):
    """
    Принимает приглашение в команду. После принятия все остальные приглашения удаляются.
    """
    return await service.accept(team_id, user_dto.user_id)


@router.delete("/{team_id}", summary="Отказ от приглашения")
async def decline_invite(
    team_id: int,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.DeclineInvite)
    ),
    service: InviteService = Depends(get_invite_service),
):
    """
    Позволяет отказаться от приглашения. По сути просто удаляет его.
    """
    return await service.decline(team_id, user_dto.user_id)

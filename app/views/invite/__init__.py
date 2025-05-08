from app.controllers.invite import InviteController, get_invite_controller
from app.views.dependencies import TeamOwnerDto, get_team_owner
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.invite.dto import TeamInviteDto
from app.controllers.auth import PermittedAction
from app.acl.permissions import Permissions
from fastapi import APIRouter, Depends


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
    controller: InviteController = Depends(get_invite_controller),
):
    """
    Возвращает список всех приглашений в команды для текущего пользователя.
    """
    return await controller.get_user_invites(user_dto.user_id)


@router.post(
    "/create/{user_id}",
    response_model=TeamInviteDto,
    summary="Приглашение пользователя",
)
async def invite_user(
    user_id: int,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    controller: InviteController = Depends(get_invite_controller),
):
    """
    Отправляет пользователю приглашение в команду.
    """
    return await controller.invite_user(owner_dto.team_dto.id, user_id)


@router.post("/{team_id}", summary="Принятие приглашения")
async def accept_invite(
    team_id: int,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.AcceptInvite)
    ),
    controller: InviteController = Depends(get_invite_controller),
):
    """
    Принимает приглашение в команду. После принятия все остальные приглашения удаляются.
    """
    return await controller.accept(team_id, user_dto.user_id)


@router.delete("/{team_id}", summary="Отказ от приглашения")
async def decline_invite(
    team_id: int,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.DeclineInvite)
    ),
    controller: InviteController = Depends(get_invite_controller),
):
    """
    Позволяет отказаться от приглашения. По сути просто удаляет его.
    """
    return await controller.decline(team_id, user_dto.user_id)

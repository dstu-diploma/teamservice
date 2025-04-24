from app.controllers.invite import InviteController, get_invite_controller
from app.views.dependencies import TeamOwnerDto, get_team_owner
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.invite.dto import TeamInviteDto
from app.controllers.auth import get_user_dto
from fastapi import APIRouter, Depends

router = APIRouter(tags=["Основное"], prefix="/invite")


@router.get("/", response_model=list[TeamInviteDto])
async def get_user_invites(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: InviteController = Depends(get_invite_controller),
):
    return await controller.get_user_invites(user_dto.user_id)


@router.post("/invite/{id}", response_model=TeamInviteDto)
async def invite_user(
    user_id: int,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    controller: InviteController = Depends(get_invite_controller),
):
    return await controller.invite_user(owner_dto.team_dto.id, user_id)


@router.post("/{id}")
async def accept_invite(
    team_id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: InviteController = Depends(get_invite_controller),
):
    return await controller.accept(team_id, user_dto.user_id)


@router.delete("/{id}")
async def decline_invite(
    team_id: int,
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: InviteController = Depends(get_invite_controller),
):
    return await controller.decline(team_id, user_dto.user_id)

from app.views.dependencies import TeamOwnerDto, get_team_owner
from fastapi import APIRouter, Depends
from app.controllers.hackathon_teams import (
    IHackathonTeamsController,
    get_hackathon_teams_controller,
)
from app.controllers.hackathon_teams.dto import (
    HackathonTeamMateDto,
    HackathonTeamWithMatesDto,
)
from app.controllers.auth.dto import AccessJWTPayloadDto
from app.controllers.auth import get_user_dto
from app.views.mate.dto import MateCaptainRightsDto
from app.views.mate.exceptions import NoMoreCaptainsException
from .dto import CreateHackathonTeamDto


router = APIRouter(tags=["Хакатоновские команды"], prefix="/hackathon")


@router.post(
    "/",
    response_model=HackathonTeamWithMatesDto,
    summary="Регистрация команды на хакатоне",
)
async def create_hackathon_team(
    create_dto: CreateHackathonTeamDto,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Регистрирует новую команду на хакатон. Данные для создания команды берутся из текущей команды пользователя.
    Текущий пользователь должен быть капитаном.

    `mate_user_ids` представляет собой список UserID участников создаваемой команды.
    Каждый из участников должен принадлежать брендовой команде пользователя.
    Если хотя бы один из пользователей уже участвует в хакатоне, то вернется 400.

    Если в хакатоне больше нет мест/в формируемой команде получается слишком много пользователей (решается конкретным хакатоном), вернет 400.
    """
    return await controller.create(
        owner_dto.team_dto.id, create_dto.hackathon_id, create_dto.mate_user_ids
    )


@router.get(
    "/my",
    response_model=HackathonTeamWithMatesDto,
    summary="Получение информации о команде пользователя",
)
async def get_my_hack_team_info(
    user_dto: AccessJWTPayloadDto = Depends(get_user_dto),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Возвращает полную информацию о хакатоновской команде текущего пользователя (если он в ней состоит).
    """
    mate = await controller.get_mate(user_dto.user_id)
    return await controller.get_total(mate.team_id)


@router.put("/mate/captain-rights", summary="Изменение прав капитанства")
async def set_mate_is_captain(
    dto: MateCaptainRightsDto,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Устанавливает права капитана пользователю.
    Текущий пользователь сам должен являться капитаном.
    Если попытаться снять права капитана с единственного участника, то вернет 400.
    """
    if (
        not dto.is_captain
        and len(await controller.get_captains(owner_dto.team_dto.id)) <= 1
    ):
        raise NoMoreCaptainsException()

    await controller.set_mate_is_captain(dto.user_id, dto.is_captain)


@router.delete(
    "/mate/{user_id}/",
    response_model=HackathonTeamMateDto,
    summary="Удаление участника",
)
async def remove_mate(
    user_id: int,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Удаляет участника хакатоновской команды. Текущий пользователь должен быть капитаном команды.
    Если в команде больше не останется участников, то она будет удалена.
    """
    return await controller.remove_mate(user_id)


@router.post(
    "/mate/{user_id}/",
    response_model=HackathonTeamMateDto,
    summary="Добавление участника",
)
async def add_mate(
    user_id: int,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Добавляет участника хакатоновской команды. Права капитанства наследуются автоматически.
    Текущий пользователь должен быть капитаном.
    """
    owner_hack_mate = await controller.get_mate(owner_dto.user_dto.user_id)
    return await controller.add_mate(
        owner_dto.team_dto.id, owner_hack_mate.team_id, user_id
    )

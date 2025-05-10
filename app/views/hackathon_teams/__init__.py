from app.views.mate.dto import MateCaptainRightsDto, MateRoleDescDto
from app.views.dependencies import TeamOwnerDto, get_team_owner
from app.views.mate.exceptions import NoMoreCaptainsException
from app.controllers.auth.dto import AccessJWTPayloadDto
from fastapi import APIRouter, Depends, UploadFile
from app.controllers.auth import PermittedAction
from app.acl.permissions import Permissions
from .dto import CreateHackathonTeamDto
from urllib.parse import quote
from uuid import uuid4
import io

from app.controllers.hackathon_team_submissions import (
    get_hackathon_team_submissions_controller,
    IHackathonTeamSubmissionsController,
)
from app.controllers.hackathon_team_submissions.dto import (
    HackathonTeamSubmissionDto,
)

from app.controllers.hackathon_teams import (
    get_hackathon_teams_controller,
    IHackathonTeamsController,
)
from app.controllers.hackathon_teams.dto import (
    HackathonTeamWithMatesDto,
    HackathonTeamMateDto,
)


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
    "/{hackathon_id}/my",
    response_model=HackathonTeamWithMatesDto,
    summary="Получение информации о команде пользователя",
)
async def get_my_hack_team_info(
    hackathon_id: int,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.CreateTeam)
    ),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Возвращает полную информацию о хакатоновской команде текущего пользователя (если он в ней состоит).
    """
    mate = await controller.get_mate(user_dto.user_id, hackathon_id)
    return await controller.get_total(mate.team_id)


@router.put(
    "/{hackathon_id}/mate/role-desc",
    response_model=HackathonTeamWithMatesDto,
    summary="Установить себе названия роли",
)
async def set_role_desc(
    hackathon_id: int,
    dto: MateRoleDescDto,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateSelf)
    ),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Устанавливает текущему пользователю описание роли (наприме: Backend/Frontend; Python, Lua).
    Текущий пользователь должен быть в команде.
    """
    return await controller.set_mate_role_desc(
        hackathon_id, user_dto.user_id, dto.role_desc
    )


@router.put(
    "/{hackathon_id}/mate/captain-rights",
    response_model=HackathonTeamMateDto,
    summary="Изменение прав капитанства",
)
async def set_mate_is_captain(
    hackathon_id: int,
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

    return await controller.set_mate_is_captain(
        hackathon_id, dto.user_id, dto.is_captain
    )


@router.delete(
    "/{hackathon_id}/mate/",
    response_model=HackathonTeamMateDto,
    summary="Удаление участника",
)
async def leave_team(
    hackathon_id: int,
    user_dto: AccessJWTPayloadDto = Depends(
        PermittedAction(Permissions.UpdateSelf)
    ),
    controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
):
    """
    Удаляет текущего пользователя из команды.
    Если в команде больше не останется участников, то она будет удалена.
    """
    current_mate = await controller.get_mate(user_dto.user_id, hackathon_id)
    return await controller.remove_mate(current_mate.team_id, user_dto.user_id)


@router.delete(
    "/{hackathon_id}/mate/{user_id}/",
    response_model=HackathonTeamMateDto,
    summary="Удаление участника",
)
async def remove_mate(
    hackathon_id: int,
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
    return await controller.remove_mate(hackathon_id, user_id)


@router.post(
    "/{hackathon_id}/mate/{user_id}/",
    response_model=HackathonTeamMateDto,
    summary="Добавление участника",
)
async def add_mate(
    hackathon_id: int,
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
    current_mate = await controller.get_mate(
        owner_dto.user_dto.user_id, hackathon_id
    )
    return await controller.add_mate(
        owner_dto.team_dto.id, current_mate.team_id, user_id
    )


@router.put(
    "/{hackathon_id}/submission",
    response_model=HackathonTeamSubmissionDto,
    summary="Загрузка результатов",
)
async def upload_submission(
    hackathon_id: int,
    file: UploadFile,
    owner_dto: TeamOwnerDto = Depends(get_team_owner),
    team_controller: IHackathonTeamsController = Depends(
        get_hackathon_teams_controller
    ),
    submission_controller: IHackathonTeamSubmissionsController = Depends(
        get_hackathon_team_submissions_controller
    ),
):
    current_mate = await team_controller.get_mate(
        owner_dto.user_dto.user_id, hackathon_id
    )
    filename = quote(f"{current_mate.team_id}_{current_mate.user_id}_{uuid4()}")

    return await submission_controller.upload_team_submission(
        hackathon_id,
        filename,
        current_mate.team_id,
        io.BytesIO(await file.read()),
    )

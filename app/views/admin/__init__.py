from app.controllers.team import TeamController, get_team_controller
from app.controllers.auth import UserWithRole
from app.controllers.team.dto import TeamDto
from fastapi import APIRouter, Depends

from app.views.admin.dto import ChangeNameDto
from app.views.root.dto import UserIdDto


router = APIRouter(
    tags=["Админка"],
    prefix="/admin",
    dependencies=(Depends(UserWithRole("admin")),),
)


@router.get("/", response_model=list[TeamDto], summary="Список всех команд")
async def get_all_teams(
    team_controller: TeamController = Depends(get_team_controller),
):
    """
    Возвращает список всех команд.
    """
    return await team_controller.get_all()


@router.post("/name", response_model=TeamDto, summary="Изменение названия")
async def change_name(
    name_dto: ChangeNameDto,
    team_controller: TeamController = Depends(get_team_controller),
):
    """
    Изменяет название команды. Название должно быть уникальным.
    """
    return await team_controller.update_name(
        name_dto.team_id, name_dto.new_name
    )


@router.delete("/{id}", summary="Удаление команды")
async def delete_team(
    id: int, team_controller: TeamController = Depends(get_team_controller)
):
    """
    Удаляет команду из списка команд.
    """
    return await team_controller.delete(id)


@router.post(
    "/{id}/change_owner",
    response_model=TeamDto,
    summary="Передача прав владельца",
)
async def change_owner(
    id: int,
    dto: UserIdDto,
    team_controller: TeamController = Depends(get_team_controller),
    summary="Передача прав владельца",
):
    """
    Изменяет ID владельца команды. Предыдущий владелец станет участником.
    """
    return await team_controller.grant_ownership(id, dto.user_id)

from app.ports.userservice.exceptions import UserDoesNotExistException
from app.acl.permissions import Permissions, perform_check
from app.ports.userservice.dto import ExternalUserDto
from app.services.mate.interface import IMateService
from app.ports.userservice import IUserServicePort
from app.services.mate.dto import TeamMateDto
from app.models.team import TeamMatesModel
import app.util.dto_utils as dto_utils
from app.acl.roles import UserRoles
from fastapi import HTTPException
from typing import cast

from app.services.mate.exceptions import (
    AlreadyTeamMemberException,
    IncorrectMateRoleException,
    NotAMemberException,
)


class MateService(IMateService):
    def __init__(self, user_service: IUserServicePort):
        self.user_service = user_service

    async def _get_mate(self, user_id: int) -> TeamMatesModel:
        mate = await TeamMatesModel.get_or_none(user_id=user_id)
        if mate is None:
            raise NotAMemberException()

        return mate

    async def _get_mate_info(self, user_id: int) -> ExternalUserDto:
        try:
            return await self.user_service.get_user_info(user_id)
        except HTTPException as e:
            raise UserDoesNotExistException()

    async def get_mate(self, user_id: int) -> TeamMateDto | None:
        mate = await TeamMatesModel.get_or_none(user_id=user_id)

        if not mate:
            return None

        user_info = await self.user_service.try_get_user_info(mate.user_id)
        dto = TeamMateDto.from_tortoise(mate)

        if user_info:
            dto.user_uploads = user_info.uploads

        return dto

    async def get_mates(self, team_id: int) -> list[TeamMateDto]:
        mates = await TeamMatesModel.filter(team_id=team_id)
        dtos = [TeamMateDto.from_tortoise(mate) for mate in mates]
        external_user_info = await self.user_service.try_get_user_info_many(
            dto_utils.export_int_fields(dtos, "user_id")
        )
        names = self.user_service.get_name_map(external_user_info)
        user_map = dict((user.id, user) for user in external_user_info)

        dtos = dto_utils.inject_mapping(
            dtos, names, "user_id", "user_name", strict=True
        )

        for dto in dtos:
            if dto.user_id in user_map:
                dto.user_uploads = user_map[dto.user_id].uploads

        return dtos

    async def get_mate_count(self, team_id: int) -> int:
        return await TeamMatesModel.filter(team_id=team_id).count()

    async def add(
        self, team_id: int, user_id: int, is_captain: bool
    ) -> TeamMateDto:
        if await self.get_mate(user_id) is not None:
            raise AlreadyTeamMemberException()

        mate_info = await self._get_mate_info(user_id)

        if not perform_check(
            Permissions.CanBeInTeam, cast(UserRoles, mate_info.role)
        ):
            raise IncorrectMateRoleException()

        mate = await TeamMatesModel.create(
            team_id=team_id, user_id=user_id, is_captain=is_captain
        )

        dto = TeamMateDto.from_tortoise(mate)
        dto.user_name = mate_info.formatted_name
        dto.user_uploads = mate_info.uploads

        return dto

    async def remove(self, user_id: int, silent: bool = False) -> TeamMateDto:
        mate_info: ExternalUserDto | None = None
        if not silent:
            mate_info = await self._get_mate_info(user_id)

        mate = await self._get_mate(user_id)
        await mate.delete()

        dto = TeamMateDto.from_tortoise(mate)

        if mate_info:
            dto.user_name = mate_info.formatted_name
            dto.user_uploads = mate_info.uploads

        return dto

    async def set_is_captain(
        self, user_id: int, is_captain: bool
    ) -> TeamMateDto:
        mate_info = await self._get_mate_info(user_id)

        mate = await self._get_mate(user_id)
        mate.is_captain = is_captain
        await mate.save()

        dto = TeamMateDto.from_tortoise(mate)
        dto.user_name = mate_info.formatted_name
        dto.user_uploads = mate_info.uploads

        return dto

    async def set_role_desc(self, user_id: int, role_desc: str) -> TeamMateDto:
        mate_info = await self._get_mate_info(user_id)

        mate = await self._get_mate(user_id)
        mate.role_desc = role_desc
        await mate.save()

        dto = TeamMateDto.from_tortoise(mate)
        dto.user_name = mate_info.formatted_name
        dto.user_uploads = mate_info.uploads

        return dto

    async def get_captains(self, team_id: int) -> list[TeamMateDto]:
        mates = await TeamMatesModel.filter(team_id=team_id, is_captain=True)
        dtos = [TeamMateDto.from_tortoise(mate) for mate in mates]
        external_user_info = await self.user_service.try_get_user_info_many(
            dto_utils.export_int_fields(dtos, "user_id")
        )
        names = self.user_service.get_name_map(external_user_info)
        user_map = dict((user.id, user) for user in external_user_info)

        dtos = dto_utils.inject_mapping(
            dtos, names, "user_id", "user_name", strict=True
        )

        for dto in dtos:
            if dto.user_id in user_map:
                dto.user_uploads = user_map[dto.user_id].uploads

        return dtos

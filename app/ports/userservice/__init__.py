from app.ports.userservice.dto import ExternalUserDto
from collections import defaultdict
from typing import Protocol

from app.ports.userservice.exceptions import UserServiceError


class IUserServicePort(Protocol):
    base_url: str

    async def get_user_info(self, user_id: int) -> ExternalUserDto: ...
    async def get_user_info_many(
        self, user_ids: frozenset[int]
    ) -> list[ExternalUserDto]: ...

    def get_name_map(
        self, users: list[ExternalUserDto]
    ) -> defaultdict[int, str | None]:
        name_map: defaultdict[int, str | None] = defaultdict(lambda: None)

        for user in users:
            name_map[user.id] = user.formatted_name

        return name_map

    async def try_get_user_info(self, user_id: int) -> ExternalUserDto | None:
        try:
            return await self.get_user_info(user_id)
        except Exception:
            return None

    async def get_user_exists(self, user_id: int) -> bool:
        try:
            return await self.get_user_info(user_id) is not None
        except UserServiceError:
            raise

    async def try_get_user_info_many(
        self, user_ids: frozenset[int]
    ) -> list[ExternalUserDto]:
        try:
            return await self.get_user_info_many(user_ids)
        except Exception:
            return []

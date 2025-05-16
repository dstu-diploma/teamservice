from app.ports.userservice.dto import MinimalUserDto
from collections import defaultdict
from typing import Protocol

from app.ports.userservice.exceptions import UserServiceError


class IUserServicePort(Protocol):
    base_url: str

    async def get_user_info(self, user_id: int) -> MinimalUserDto: ...
    async def get_user_info_many(
        self, user_ids: frozenset[int]
    ) -> list[MinimalUserDto]: ...

    def format_name(self, user: MinimalUserDto) -> str:
        return f"{user.last_name} {user.first_name} {user.patronymic}"

    def get_name_map(
        self, users: list[MinimalUserDto]
    ) -> defaultdict[int, str | None]:
        name_map: defaultdict[int, str | None] = defaultdict(lambda: None)

        for user in users:
            full_name = self.format_name(user)
            name_map[user.id] = full_name

        return name_map

    async def try_get_user_info(self, user_id: int) -> MinimalUserDto | None:
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
    ) -> list[MinimalUserDto]:
        try:
            return await self.try_get_user_info_many(user_ids)
        except Exception:
            return []

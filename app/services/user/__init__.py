from .exceptions import UserServiceError
from functools import lru_cache
from app.config import Settings
from fastapi import Depends
from typing import Protocol
import httpx


class IUserService(Protocol):
    async def get_user_exists(self, user_id: int) -> bool: ...


class UserService(IUserService):
    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.client = client
        self.base_url = Settings.USER_SERVICE_URL
        self.headers = {
            "Authorization": f"Bearer {Settings.USER_SERVICE_API_KEY}"
        }

    async def get_user_exists(self, user_id: int) -> bool:
        url = f"{self.base_url}/{user_id}"

        try:
            response = await self.client.get(url, headers=self.headers)
            return response.status_code == 200
        except httpx.HTTPError as e:
            raise UserServiceError()


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


@lru_cache
def get_user_service(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> UserService:
    return UserService(client=client)

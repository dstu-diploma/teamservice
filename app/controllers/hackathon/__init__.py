from .exceptions import HackathonServiceError
from functools import lru_cache
from .dto import HackathonDto
from fastapi import Depends, HTTPException
from typing import Protocol
from os import environ
import httpx

HACKATHON_SERVICE_URL = environ.get("HACKATHON_SERVICE_URL")
HACKATHON_SERVICE_API_KEY = environ.get("HACKATHON_SERVICE_API_KEY")


class IHackathonController(Protocol):
    async def get_hackathon_data(self, hackathon_id: int) -> HackathonDto: ...
    async def can_edit_team_registry(self, hackathon_id: int) -> bool: ...
    async def can_upload_submissions(self, hackathon_id: int) -> bool: ...


class HackathonController(IHackathonController):
    def __init__(
        self,
        client: httpx.AsyncClient,
    ):
        self.client = client
        self.base_url = HACKATHON_SERVICE_URL
        self.headers = {"Authorization": f"Bearer {HACKATHON_SERVICE_API_KEY}"}

    async def _do_get(self, url: str) -> dict:
        try:
            response = await self.client.get(url, headers=self.headers)
            data = response.json()
            if response.status_code == 200:
                return data
            else:
                raise HTTPException(
                    status_code=response.status_code, detail=data["detail"]
                )
        except httpx.HTTPError as e:
            raise HackathonServiceError()

    async def get_hackathon_data(self, hackathon_id: int) -> HackathonDto:
        data = await self._do_get(f"{self.base_url}/{hackathon_id}")
        return HackathonDto(**data)

    async def can_edit_team_registry(self, hackathon_id: int) -> bool:
        data = await self._do_get(
            f"{self.base_url}/{hackathon_id}/can-edit-team-registry"
        )
        return data["can_edit"]

    async def can_upload_submissions(self, hackathon_id: int) -> bool:
        data = await self._do_get(
            f"{self.base_url}/{hackathon_id}/can-upload-submissions"
        )
        return data["can_upload"]


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


@lru_cache
def get_hackathon_controller(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> HackathonController:
    return HackathonController(client=client)

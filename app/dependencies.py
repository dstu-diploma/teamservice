from app.adapters.event_consumer.aiopika import AioPikaEventConsumerAdapter
from app.adapters.event_publisher.aiopika import AioPikaEventPublisherAdapter
from app.ports.event_consumer import IEventConsumerPort
from app.services.hackathon_teams.interface import IHackathonTeamsService
from app.services.hackathon_teams.service import HackathonTeamsService
from app.adapters.hackathonservice import HackathonServiceAdapter
from app.ports.hackathonservice import IHackathonServicePort
from app.services.brand_team.interface import ITeamService
from app.ports.event_publisher import IEventPublisherPort
from app.services.invite.interface import IInviteService
from app.adapters.userservice import UserServiceAdapter
from app.services.brand_team.service import TeamService
from app.services.invite.service import InviteService
from app.services.mate.interface import IMateService
from app.ports.userservice import IUserServicePort
from app.services.mate.service import MateService
from app.adapters.storage import S3StorageAdapter
from app.ports.storage import IStoragePort
from app.config import Settings
from functools import lru_cache
from fastapi import Depends
import httpx

from app.services.hackathon_team_submissions.interface import (
    IHackathonTeamSubmissionsService,
)
from app.services.hackathon_team_submissions.service import (
    HackathonTeamSubmissionsService,
)


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


@lru_cache
def get_storage() -> IStoragePort:
    return S3StorageAdapter()


@lru_cache
def get_event_publisher() -> IEventPublisherPort:
    return AioPikaEventPublisherAdapter(Settings.RABBITMQ_URL, "events")


@lru_cache
def get_event_consumer() -> IEventConsumerPort:
    return AioPikaEventConsumerAdapter(
        Settings.RABBITMQ_URL, "events", queue_name="teamservice"
    )


@lru_cache
def get_user_service(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> IUserServicePort:
    return UserServiceAdapter(client)


@lru_cache
def get_hackathon_service(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> IHackathonServicePort:
    return HackathonServiceAdapter(client=client)


@lru_cache
def get_mate_service(
    user_service: IUserServicePort = Depends(get_user_service),
) -> IMateService:
    return MateService(user_service)


@lru_cache
def get_team_service(
    user_service: IUserServicePort = Depends(get_user_service),
    mate_service: IMateService = Depends(get_mate_service),
) -> ITeamService:
    return TeamService(user_service, mate_service)


@lru_cache
def get_invite_service(
    team_service: ITeamService = Depends(get_team_service),
    mate_service: IMateService = Depends(get_mate_service),
) -> IInviteService:
    return InviteService(
        team_service=team_service,
        user_service=team_service.user_service,
        mate_service=mate_service,
    )


@lru_cache
def get_hackathon_team_submissions_service(
    hackathon_service: IHackathonServicePort = Depends(get_hackathon_service),
    storage: IStoragePort = Depends(get_storage),
) -> IHackathonTeamSubmissionsService:
    return HackathonTeamSubmissionsService(hackathon_service, storage)


@lru_cache
def get_hackathon_teams_service(
    hackathon_service: IHackathonServicePort = Depends(get_hackathon_service),
    brand_mate_service: IMateService = Depends(get_mate_service),
    brand_team_service: ITeamService = Depends(get_team_service),
    submission_service: IHackathonTeamSubmissionsService = Depends(
        get_hackathon_team_submissions_service
    ),
    user_service: IUserServicePort = Depends(get_user_service),
) -> IHackathonTeamsService:
    return HackathonTeamsService(
        hackathon_service=hackathon_service,
        brand_mate_service=brand_mate_service,
        brand_team_service=brand_team_service,
        submission_service=submission_service,
        user_service=user_service,
    )

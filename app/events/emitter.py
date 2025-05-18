from pyee.asyncio import AsyncIOEventEmitter
from enum import StrEnum


class Events(StrEnum):
    UserBanned = "user.banned"
    UserDeleted = "user.deleted"
    TeamHackathonTeamDeleted = "team.hackathon_team_deleted"


Emitter = AsyncIOEventEmitter()

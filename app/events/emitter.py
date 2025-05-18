from pyee.asyncio import AsyncIOEventEmitter
from enum import StrEnum


class Events(StrEnum):
    UserBanned = "user.banned"
    UserDeleted = "user.deleted"


Emitter = AsyncIOEventEmitter()

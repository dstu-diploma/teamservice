from app.controllers.auth.dto import AccessJWTPayloadDto
from jose import ExpiredSignatureError, JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Annotated
from fastapi import Depends
from os import environ
from .exceptions import (
    InvalidTokenException,
    RestrictedRolesException,
    JWTParseErrorException,
    TokenExpiredException,
)


JWT_SECRET = environ.get("JWT_SECRET", "dstu")
SECURITY_SCHEME = HTTPBearer(auto_error=False)


class UserJWTDto(BaseModel):
    access_token: str
    refresh_token: str


def get_token_from_header(
    credentials: HTTPAuthorizationCredentials = Depends(SECURITY_SCHEME),
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise InvalidTokenException()
    return credentials.credentials


async def get_user_dto(
    token: str = Depends(get_token_from_header),
) -> AccessJWTPayloadDto:
    try:
        raw_payload = jwt.decode(token, JWT_SECRET)
        return AccessJWTPayloadDto(**raw_payload)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise JWTParseErrorException()


class UserWithRole:
    allowed_roles: tuple[str, ...]
    allowed_roles_str: str

    def __init__(self, *allowed_roles: str):
        self.allowed_roles = allowed_roles
        self.allowed_roles_str = ", ".join(allowed_roles)

    def __call__(
        self, user_dto: Annotated[AccessJWTPayloadDto, Depends(get_user_dto)]
    ) -> AccessJWTPayloadDto:
        if user_dto.role in self.allowed_roles:
            return user_dto
        else:
            raise RestrictedRolesException(self.allowed_roles_str)

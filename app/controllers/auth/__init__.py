from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.acl.permissions import PermissionAcl, perform_check
from app.controllers.auth.dto import AccessJWTPayloadDto
from jose import ExpiredSignatureError, JWTError, jwt
from app.config import Settings
from pydantic import BaseModel
from typing import Annotated
from fastapi import Depends

from .exceptions import (
    InvalidTokenException,
    RestrictedPermissionException,
    JWTParseErrorException,
    TokenExpiredException,
)


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
        raw_payload = jwt.decode(token, Settings.JWT_SECRET)
        return AccessJWTPayloadDto(**raw_payload)
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise JWTParseErrorException()


class PermittedAction:
    acl: PermissionAcl

    def __init__(self, acl: PermissionAcl):
        self.acl = acl

    def __call__(
        self, user_dto: Annotated[AccessJWTPayloadDto, Depends(get_user_dto)]
    ):
        if perform_check(self.acl, user_dto.role):
            return user_dto

        raise RestrictedPermissionException()

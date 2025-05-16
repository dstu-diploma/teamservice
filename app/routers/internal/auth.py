from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .exceptions import InvalidAuthException
from app.config import Settings
from fastapi import Depends


SECURITY_SCHEME = HTTPBearer(auto_error=False)


def get_token_from_header(
    credentials: HTTPAuthorizationCredentials = Depends(SECURITY_SCHEME),
) -> str:
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
        or credentials.credentials != Settings.INTERNAL_API_KEY
    ):
        raise InvalidAuthException()
    return credentials.credentials

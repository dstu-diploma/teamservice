from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .exceptions import InvalidAuthException
from fastapi import Depends
from os import environ


SECURITY_SCHEME = HTTPBearer(auto_error=False)
API_KEY = environ.get("INTERNAL_API_KEY", "apikey")


def get_token_from_header(
    credentials: HTTPAuthorizationCredentials = Depends(SECURITY_SCHEME),
) -> str:
    if (
        credentials is None
        or credentials.scheme.lower() != "bearer"
        or credentials.credentials != API_KEY
    ):
        raise InvalidAuthException()
    return credentials.credentials

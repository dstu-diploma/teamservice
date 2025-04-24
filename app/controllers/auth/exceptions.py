from fastapi import HTTPException


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Необходимо передать Bearer-токен в заголовок Authorization!",
        )


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Истек срок действия токена!")


class JWTParseErrorException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Произошла ошибка при считывании JWT-токена!",
        )


class RestrictedRolesException(HTTPException):
    def __init__(self, allowed_roles_str: str):
        super().__init__(
            status_code=403,
            detail=f"У Вас недостаточно прав. Действие разрешено следующим ролям: {allowed_roles_str}",
        )

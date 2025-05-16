from fastapi import HTTPException


class UserDoesNotExistException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Пользователя с данным ID не существует!"
        )


class UserServiceError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Произошла ошибка при попытке обратиться к сервису пользователей!",
        )

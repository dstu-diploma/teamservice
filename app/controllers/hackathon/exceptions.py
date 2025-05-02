from fastapi import HTTPException


class HackathonServiceError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Произошла ошибка при попытке обратиться к сервису хакатонов!",
        )

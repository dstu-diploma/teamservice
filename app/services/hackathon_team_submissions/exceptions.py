from fastapi import HTTPException


class HackathonTeamCantUploadSubmissionsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Загружать результаты можно только до начала периода оценивания!",
        )


class HackathonFileTypeRestrictedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данный тип файла запрещен к загрузке!",
        )

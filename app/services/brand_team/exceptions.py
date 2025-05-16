from fastapi import HTTPException


class TeamDoesNotExistException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Команды с таким ID не существует!"
        )


class TeamNameAlreadyUsedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Данное название команды уже занято!"
        )


class UserNotInTeamException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данный пользователь не является членом какой-либо команды!",
        )


class UserIsNotOwnerOfTeamException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данный пользователь не является владельцем какой-либо команды!",
        )

from fastapi import HTTPException


class AlreadyTeamMemberException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данный пользователь уже является членом команды!",
        )


class NotAMemberException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данный пользователь не входит ни в какую команду!",
        )


class IncorrectMateRoleException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Роль пользователя не имеет права участвовать в командах!",
        )

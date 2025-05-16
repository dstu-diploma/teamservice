from fastapi import HTTPException


class UserAlreadyInvitedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данный пользователь уже приглашен в эту команду!",
        )


class NoSuchInviteException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данный пользователь не приглашался в эту команду!",
        )

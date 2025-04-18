from fastapi import HTTPException


class UserAlreadyInvitedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="User is already invited to the team!"
        )


class NoSuchInviteException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Cant find invite for that user in the team!",
        )

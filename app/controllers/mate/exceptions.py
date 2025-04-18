from fastapi import HTTPException


class AlreadyTeamMemberException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="User is already member of a group!"
        )


class NotAMemberException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="User is not a member of any group!"
        )

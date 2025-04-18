from fastapi import HTTPException


class TeamDoesNotExistException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No team with such id!")


class AlreadyTeamMemberException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Current user is already member of a group!"
        )


class AlreadyTeamOwnerException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Current user is already owner of a group!"
        )


class TeamNameAlreadyUsedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="This team name already used!")


class UserNotInTeamException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Current user is not member of any group!"
        )


class UserIsNotOwnerOfGroupException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="Current user is not owner of any group!"
        )

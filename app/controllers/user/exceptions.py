from fastapi import HTTPException


class UserDoesNotExistException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="No user with such id!")

from fastapi import HTTPException


class InvalidAuthException(HTTPException):
    def __init__(self):
        self.status_code = 403
        self.detail = "Invalid auth!"

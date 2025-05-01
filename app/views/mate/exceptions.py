from fastapi import HTTPException


class NoMoreCaptainsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Вы не можете снять права капитана с единственного участника!",
        )

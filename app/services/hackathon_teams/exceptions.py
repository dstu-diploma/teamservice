from fastapi import HTTPException


class CantEditHackathonTeamsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="В данном хакатоне больше нельзя менять состав команд!",
        )


class ThisBrandTeamAlreadyParticipatesException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Ваша команда-бренд уже участвует в данном хакатоне!",
        ),


class CantCreateEmptyTeamException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Команда не может существовать без участников!",
        )


class UserAlreadyParticipatingInHackathonException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail=f"Один из пользователей уже участвует в данном хакатоне!",
        )


class CantMakeSuchLargeTeamException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="В данном хакатоне нельзя делать такую большую команду!",
        )


class TeamDoesNotFitHackathonException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данная команда не вмещается в список участников хакатона!",
        )


class MateTeamMismatchException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Данный пользователь принадлежит другой команде!",
        )


class CantCreateTeamWithoutCaptainException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Невозможно создать команду без капитана!",
        )

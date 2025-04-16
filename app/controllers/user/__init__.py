from typing import Protocol


class IUserController(Protocol):
    async def get_user_exists(self, user_id: int) -> bool: ...


# TODO: связь с UserService
class UserController(IUserController):
    def __init__(self):
        pass

    async def get_user_exists(self, user_id: int) -> bool:
        return True

from enum import StrEnum


class UserRoles(StrEnum):
    User = "user"
    Organizer = "organizer"
    Helper = "helper"
    Judge = "judge"
    Admin = "admin"

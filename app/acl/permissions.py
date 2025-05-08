from .roles import UserRoles


class PublicAccess:
    pass


class Group:
    members: frozenset[UserRoles]

    def __init__(self, *members: UserRoles):
        self.members = frozenset(members)


PermissionAcl = UserRoles | Group | PublicAccess


class Permissions:
    __PRIVILEGED = Group(UserRoles.Organizer, UserRoles.Admin)

    CanBeInTeam = UserRoles.User
    UpdateSelf = UserRoles.User
    CreateTeam = UserRoles.User
    GetTeamInfo = PublicAccess()

    AcceptInvite = UserRoles.User
    DeclineInvite = PublicAccess()

    GetAllTeams = __PRIVILEGED

    UpdateBrandTeam = __PRIVILEGED
    DeleteBrandTeam = __PRIVILEGED

    UpdateHackathonTeam = __PRIVILEGED
    DeleteHackathonTeam = __PRIVILEGED


def perform_check(acl: PermissionAcl, role: UserRoles) -> bool:
    if isinstance(acl, PublicAccess):
        return True
    elif isinstance(acl, UserRoles):
        return role is acl

    return role in acl.members

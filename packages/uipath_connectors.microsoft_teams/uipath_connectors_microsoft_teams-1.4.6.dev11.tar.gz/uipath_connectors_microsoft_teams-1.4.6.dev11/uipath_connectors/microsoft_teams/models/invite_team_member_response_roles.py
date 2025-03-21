from enum import Enum


class InviteTeamMemberResponseRoles(str, Enum):
    GUEST = "Guest"
    OWNER = "Owner"

    def __str__(self) -> str:
        return str(self.value)

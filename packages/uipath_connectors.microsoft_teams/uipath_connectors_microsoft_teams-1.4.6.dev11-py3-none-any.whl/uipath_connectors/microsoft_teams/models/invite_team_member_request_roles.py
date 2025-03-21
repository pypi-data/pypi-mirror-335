from enum import Enum


class InviteTeamMemberRequestRoles(str, Enum):
    GUEST = "Guest"
    OWNER = "Owner"

    def __str__(self) -> str:
        return str(self.value)

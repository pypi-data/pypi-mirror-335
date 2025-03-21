from enum import Enum


class CreateOneOnOneChatRequestRoles(str, Enum):
    GUEST = "Guest"
    OWNER = "Owner"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class CreateIndividualChatMessageRequestRoles(str, Enum):
    GUEST = "Guest"
    OWNER = "Owner"

    def __str__(self) -> str:
        return str(self.value)

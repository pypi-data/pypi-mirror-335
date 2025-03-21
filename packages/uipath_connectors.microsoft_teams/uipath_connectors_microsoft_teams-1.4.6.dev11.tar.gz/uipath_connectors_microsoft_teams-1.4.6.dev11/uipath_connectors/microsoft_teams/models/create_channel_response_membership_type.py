from enum import Enum


class CreateChannelResponseMembershipType(str, Enum):
    PRIVATE = "Private"
    STANDARD = "Standard"

    def __str__(self) -> str:
        return str(self.value)

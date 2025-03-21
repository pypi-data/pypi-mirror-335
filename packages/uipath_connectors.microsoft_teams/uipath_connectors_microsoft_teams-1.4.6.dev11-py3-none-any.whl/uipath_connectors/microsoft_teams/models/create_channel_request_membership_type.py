from enum import Enum


class CreateChannelRequestMembershipType(str, Enum):
    PRIVATE = "Private"
    STANDARD = "Standard"

    def __str__(self) -> str:
        return str(self.value)

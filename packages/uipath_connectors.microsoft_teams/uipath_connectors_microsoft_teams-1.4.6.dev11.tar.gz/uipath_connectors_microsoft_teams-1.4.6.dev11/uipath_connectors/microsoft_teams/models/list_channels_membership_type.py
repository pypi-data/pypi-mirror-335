from enum import Enum


class ListChannelsMembershipType(str, Enum):
    PRIVATE = "Private"
    STANDARD = "Standard"

    def __str__(self) -> str:
        return str(self.value)

from enum import Enum


class CreateOnlineTeamsMeetingResponseAllowMeetingChat(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    LIMITED = "limited"

    def __str__(self) -> str:
        return str(self.value)

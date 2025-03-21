from enum import Enum


class CreateOnlineTeamsMeetingRequestAllowMeetingChat(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    LIMITED = "limited"

    def __str__(self) -> str:
        return str(self.value)

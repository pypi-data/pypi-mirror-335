from enum import Enum


class CreateOnlineTeamsMeetingRequestAllowedPresenters(str, Enum):
    EVERYONE = "everyone"
    ORGANIZATION = "organization"
    ORGANIZER = "organizer"
    ROLE_IS_PRESENTER = "roleIsPresenter"

    def __str__(self) -> str:
        return str(self.value)

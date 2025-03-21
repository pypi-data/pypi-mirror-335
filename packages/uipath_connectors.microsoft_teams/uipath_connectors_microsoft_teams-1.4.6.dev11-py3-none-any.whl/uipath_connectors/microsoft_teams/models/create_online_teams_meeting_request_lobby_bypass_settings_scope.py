from enum import Enum


class CreateOnlineTeamsMeetingRequestLobbyBypassSettingsScope(str, Enum):
    EVERYONE = "everyone"
    INVITED = "invited"
    ORGANIZATION = "organization"
    ORGANIZATION_AND_FEDERATED = "organizationAndFederated"
    ORGANIZATION_EXCLUDING_GUESTS = "organizationExcludingGuests"
    ORGANIZER = "organizer"

    def __str__(self) -> str:
        return str(self.value)

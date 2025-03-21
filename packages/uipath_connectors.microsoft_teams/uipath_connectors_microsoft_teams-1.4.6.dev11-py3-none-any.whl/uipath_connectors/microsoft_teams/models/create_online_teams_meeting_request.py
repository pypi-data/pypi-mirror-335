from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_online_teams_meeting_request_allow_meeting_chat import (
    CreateOnlineTeamsMeetingRequestAllowMeetingChat,
)
from ..models.create_online_teams_meeting_request_allowed_presenters import (
    CreateOnlineTeamsMeetingRequestAllowedPresenters,
)
from ..models.create_online_teams_meeting_request_lobby_bypass_settings import (
    CreateOnlineTeamsMeetingRequestLobbyBypassSettings,
)
import datetime


class CreateOnlineTeamsMeetingRequest(BaseModel):
    """
    Attributes:
        end_date_time (datetime.datetime): The meeting end time Example: 2024-04-23T18:00:34Z.
        start_date_time (datetime.datetime): The meeting start time Example: 2024-04-23T17:00:34Z.
        subject (str): The subject of the online meeting Example: Teams meeting.
        allow_attendee_to_enable_camera (Optional[bool]): Indicates whether attendees can turn on their camera or not
                Example: True.
        allow_attendee_to_enable_mic (Optional[bool]): Indicates whether attendees can turn on their microphone or not
                Example: True.
        allow_meeting_chat (Optional[CreateOnlineTeamsMeetingRequestAllowMeetingChat]): Specifies the mode of meeting
                chat Example: enabled.
        allow_new_time_proposals (Optional[bool]): Allows participants to propose new times for the event.
        allow_teamwork_reactions (Optional[bool]): Indicates whether teams reactions are enabled for the meeting or not
                Example: True.
        allowed_presenters (Optional[CreateOnlineTeamsMeetingRequestAllowedPresenters]): Specifies who can be a
                presenter in a meeting Example: everyone.
        content (Optional[str]): The main content or description of the event
        is_entry_exit_announced (Optional[bool]): Indicates whether to announce when callers join or leave Example:
                True.
        lobby_bypass_settings (Optional[CreateOnlineTeamsMeetingRequestLobbyBypassSettings]):
        optional_attendees (Optional[list[str]]):
        record_automatically (Optional[bool]): Indicates whether to record the meeting automatically Example: True.
        required_attendees (Optional[list[str]]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    end_date_time: datetime.datetime = Field(alias="endDateTime")
    start_date_time: datetime.datetime = Field(alias="startDateTime")
    subject: str = Field(alias="subject")
    allow_attendee_to_enable_camera: Optional[bool] = Field(
        alias="allowAttendeeToEnableCamera", default=None
    )
    allow_attendee_to_enable_mic: Optional[bool] = Field(
        alias="allowAttendeeToEnableMic", default=None
    )
    allow_meeting_chat: Optional["CreateOnlineTeamsMeetingRequestAllowMeetingChat"] = (
        Field(alias="allowMeetingChat", default=None)
    )
    allow_new_time_proposals: Optional[bool] = Field(
        alias="allowNewTimeProposals", default=None
    )
    allow_teamwork_reactions: Optional[bool] = Field(
        alias="allowTeamworkReactions", default=None
    )
    allowed_presenters: Optional["CreateOnlineTeamsMeetingRequestAllowedPresenters"] = (
        Field(alias="allowedPresenters", default=None)
    )
    content: Optional[str] = Field(alias="content", default=None)
    is_entry_exit_announced: Optional[bool] = Field(
        alias="isEntryExitAnnounced", default=None
    )
    lobby_bypass_settings: Optional[
        "CreateOnlineTeamsMeetingRequestLobbyBypassSettings"
    ] = Field(alias="lobbyBypassSettings", default=None)
    optional_attendees: Optional[list[str]] = Field(
        alias="optionalAttendees", default=None
    )
    record_automatically: Optional[bool] = Field(
        alias="recordAutomatically", default=None
    )
    required_attendees: Optional[list[str]] = Field(
        alias="requiredAttendees", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateOnlineTeamsMeetingRequest"], src_dict: Dict[str, Any]
    ):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.getonline_meetings_response_chat_info import (
    GetonlineMeetingsResponseChatInfo,
)
from ..models.getonline_meetings_response_join_information import (
    GetonlineMeetingsResponseJoinInformation,
)
from ..models.getonline_meetings_response_join_meeting_id_settings import (
    GetonlineMeetingsResponseJoinMeetingIdSettings,
)
from ..models.getonline_meetings_response_lobby_bypass_settings import (
    GetonlineMeetingsResponseLobbyBypassSettings,
)
from ..models.getonline_meetings_response_participants import (
    GetonlineMeetingsResponseParticipants,
)
import datetime


class GetonlineMeetingsResponse(BaseModel):
    """
    Attributes:
        allow_attendee_to_enable_camera (Optional[bool]): Permit attendees to turn on their camera during the meeting.
                Example: True.
        allow_attendee_to_enable_mic (Optional[bool]): Permit attendees to turn on their microphone during the meeting.
                Example: True.
        allow_breakout_rooms (Optional[bool]): Option to enable breakout rooms for the meeting. Example: True.
        allow_live_share (Optional[str]): Determines if participants can share content live during the meeting. Example:
                enabled.
        allow_meeting_chat (Optional[str]): Enable or disable the chat functionality during the meeting. Example:
                enabled.
        allow_participants_to_change_name (Optional[bool]): Permit participants to alter their display name in the
                meeting.
        allow_powerpoint_sharing (Optional[bool]): Enable participants to share PowerPoint presentations. Example: True.
        allow_recording (Optional[bool]): Permit participants to record the meeting. Example: True.
        allow_teamwork_reactions (Optional[bool]): Allow participants to use reactions during the meeting. Example:
                True.
        allow_transcription (Optional[bool]): Allow the meeting to be transcribed in real-time. Example: True.
        allow_whiteboard (Optional[bool]): Allow participants to use the whiteboard during the meeting. Example: True.
        allowed_presenters (Optional[str]): Defines who is allowed to present in the meeting. Example: everyone.
        auto_admitted_users (Optional[str]): Controls which participants get admitted to the meeting automatically.
                Example: everyoneInCompany.
        chat_info (Optional[GetonlineMeetingsResponseChatInfo]):
        creation_date_time (Optional[datetime.datetime]): The date and time when the meeting was created. Example:
                2024-08-13T09:20:16.2764149Z.
        end_date_time (Optional[datetime.datetime]): The date and time when the meeting is scheduled to end. Example:
                2024-04-27T14:45:00Z.
        id (Optional[str]): A unique identifier for the online meeting. Example: MSoxMTg0N2U5NC00OTI3LTRhMmQtOGE0OC1jNDY
                1ODk1OWQ4ODMqMCoqMTk6bWVldGluZ19ZemM1TjJSaE1ERXROakZtTnkwME1XTXdMV0ZpTXpZdE5UYzFaRE5rT0RRMU9XWTBAdGhyZWFkLnYy.
        is_broadcast (Optional[bool]): Indicates if the meeting is a live event broadcast.
        is_entry_exit_announced (Optional[bool]): Announce when participants join or leave the meeting. Example: True.
        join_information (Optional[GetonlineMeetingsResponseJoinInformation]):
        join_meeting_id_settings (Optional[GetonlineMeetingsResponseJoinMeetingIdSettings]):
        join_url (Optional[str]): The web address used to join the online meeting. Example:
                https://teams.microsoft.com/l/meetup-join/19%3ameeting_Yzc5N2RhMDEtNjFmNy00MWMwLWFiMzYtNTc1ZDNkODQ1OWY0%40thread
                .v2/0?context=%7b%22Tid%22%3a%222999126d-261b-4dfd-a3fb-65e7cd9a4db0%22%2c%22Oid%22%3a%2211847e94-4927-4a2d-
                8a48-c4658959d883%22%7d.
        join_web_url (Optional[str]): The URL to join the meeting via a web browser. Example:
                https://teams.microsoft.com/l/meetup-join/19%3ameeting_Yzc5N2RhMDEtNjFmNy00MWMwLWFiMzYtNTc1ZDNkODQ1OWY0%40thread
                .v2/0?context=%7b%22Tid%22%3a%222999126d-261b-4dfd-a3fb-65e7cd9a4db0%22%2c%22Oid%22%3a%2211847e94-4927-4a2d-
                8a48-c4658959d883%22%7d.
        lobby_bypass_settings (Optional[GetonlineMeetingsResponseLobbyBypassSettings]):
        meeting_code (Optional[str]): Unique code used to join the online meeting. Example: 269110949357.
        participants (Optional[GetonlineMeetingsResponseParticipants]):
        record_automatically (Optional[bool]): Indicates if the meeting should be recorded automatically.
        share_meeting_chat_history_default (Optional[str]): Set the default behavior for sharing chat history in new
                meetings. Example: none.
        start_date_time (Optional[datetime.datetime]): The scheduled date and time when the meeting is set to begin.
                Example: 2024-04-27T13:45:00Z.
        subject (Optional[str]): The title or topic of the online meeting. Example: Stduio test.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_attendee_to_enable_camera: Optional[bool] = Field(
        alias="allowAttendeeToEnableCamera", default=None
    )
    allow_attendee_to_enable_mic: Optional[bool] = Field(
        alias="allowAttendeeToEnableMic", default=None
    )
    allow_breakout_rooms: Optional[bool] = Field(
        alias="allowBreakoutRooms", default=None
    )
    allow_live_share: Optional[str] = Field(alias="allowLiveShare", default=None)
    allow_meeting_chat: Optional[str] = Field(alias="allowMeetingChat", default=None)
    allow_participants_to_change_name: Optional[bool] = Field(
        alias="allowParticipantsToChangeName", default=None
    )
    allow_powerpoint_sharing: Optional[bool] = Field(
        alias="allowPowerpointSharing", default=None
    )
    allow_recording: Optional[bool] = Field(alias="allowRecording", default=None)
    allow_teamwork_reactions: Optional[bool] = Field(
        alias="allowTeamworkReactions", default=None
    )
    allow_transcription: Optional[bool] = Field(
        alias="allowTranscription", default=None
    )
    allow_whiteboard: Optional[bool] = Field(alias="allowWhiteboard", default=None)
    allowed_presenters: Optional[str] = Field(alias="allowedPresenters", default=None)
    auto_admitted_users: Optional[str] = Field(alias="autoAdmittedUsers", default=None)
    chat_info: Optional["GetonlineMeetingsResponseChatInfo"] = Field(
        alias="chatInfo", default=None
    )
    creation_date_time: Optional[datetime.datetime] = Field(
        alias="creationDateTime", default=None
    )
    end_date_time: Optional[datetime.datetime] = Field(
        alias="endDateTime", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    is_broadcast: Optional[bool] = Field(alias="isBroadcast", default=None)
    is_entry_exit_announced: Optional[bool] = Field(
        alias="isEntryExitAnnounced", default=None
    )
    join_information: Optional["GetonlineMeetingsResponseJoinInformation"] = Field(
        alias="joinInformation", default=None
    )
    join_meeting_id_settings: Optional[
        "GetonlineMeetingsResponseJoinMeetingIdSettings"
    ] = Field(alias="joinMeetingIdSettings", default=None)
    join_url: Optional[str] = Field(alias="joinUrl", default=None)
    join_web_url: Optional[str] = Field(alias="joinWebUrl", default=None)
    lobby_bypass_settings: Optional["GetonlineMeetingsResponseLobbyBypassSettings"] = (
        Field(alias="lobbyBypassSettings", default=None)
    )
    meeting_code: Optional[str] = Field(alias="meetingCode", default=None)
    participants: Optional["GetonlineMeetingsResponseParticipants"] = Field(
        alias="participants", default=None
    )
    record_automatically: Optional[bool] = Field(
        alias="recordAutomatically", default=None
    )
    share_meeting_chat_history_default: Optional[str] = Field(
        alias="shareMeetingChatHistoryDefault", default=None
    )
    start_date_time: Optional[datetime.datetime] = Field(
        alias="startDateTime", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetonlineMeetingsResponse"], src_dict: Dict[str, Any]):
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

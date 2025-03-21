from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_online_teams_meeting_response_allow_meeting_chat import (
    CreateOnlineTeamsMeetingResponseAllowMeetingChat,
)
from ..models.create_online_teams_meeting_response_allowed_presenters import (
    CreateOnlineTeamsMeetingResponseAllowedPresenters,
)
from ..models.create_online_teams_meeting_response_chat_info import (
    CreateOnlineTeamsMeetingResponseChatInfo,
)
from ..models.create_online_teams_meeting_response_join_information import (
    CreateOnlineTeamsMeetingResponseJoinInformation,
)
from ..models.create_online_teams_meeting_response_join_meeting_id_settings import (
    CreateOnlineTeamsMeetingResponseJoinMeetingIdSettings,
)
from ..models.create_online_teams_meeting_response_lobby_bypass_settings import (
    CreateOnlineTeamsMeetingResponseLobbyBypassSettings,
)
from ..models.create_online_teams_meeting_response_participants import (
    CreateOnlineTeamsMeetingResponseParticipants,
)
import datetime


class CreateOnlineTeamsMeetingResponse(BaseModel):
    """
    Attributes:
        end_date_time (datetime.datetime): The meeting end time Example: 2024-04-23T18:00:34Z.
        start_date_time (datetime.datetime): The meeting start time Example: 2024-04-23T17:00:34Z.
        subject (str): The subject of the online meeting Example: Teams meeting.
        allow_attendee_to_enable_camera (Optional[bool]): Indicates whether attendees can turn on their camera or not
                Example: True.
        allow_attendee_to_enable_mic (Optional[bool]): Indicates whether attendees can turn on their microphone or not
                Example: True.
        allow_meeting_chat (Optional[CreateOnlineTeamsMeetingResponseAllowMeetingChat]): Specifies the mode of meeting
                chat Example: enabled.
        allow_participants_to_change_name (Optional[bool]): Indicates if participants can change their display name in
                the meeting.
        allow_recording (Optional[bool]): Indicates if recording the meeting is allowed. Example: True.
        allow_teamwork_reactions (Optional[bool]): Indicates whether teams reactions are enabled for the meeting or not
                Example: True.
        allow_transcription (Optional[bool]): Indicates if transcription is permitted during the event. Example: True.
        allowed_presenters (Optional[CreateOnlineTeamsMeetingResponseAllowedPresenters]): Specifies who can be a
                presenter in a meeting Example: everyone.
        auto_admitted_users (Optional[str]): Defines which users are automatically admitted to the meeting. Example:
                everyoneInCompany.
        chat_info (Optional[CreateOnlineTeamsMeetingResponseChatInfo]):
        creation_date_time (Optional[datetime.datetime]): The date and time when the event was created. Example:
                2024-04-28T08:57:22.9964686Z.
        id (Optional[str]): A unique identifier for the event. Example: MSoxMTg0N2U5NC00OTI3LTRhMmQtOGE0OC1jNDY1ODk1OWQ4
                ODMqMCoqMTk6bWVldGluZ19Oek0xTm1JeVptTXRNVGRtTnkwMFpUVXdMVGhtTnpVdE56RXpNbVE0WWpsa05UVTRAdGhyZWFkLnYy.
        is_broadcast (Optional[bool]): Indicates if the event is a live broadcast.
        is_entry_exit_announced (Optional[bool]): Indicates whether to announce when callers join or leave Example:
                True.
        join_information (Optional[CreateOnlineTeamsMeetingResponseJoinInformation]):
        join_meeting_id_settings (Optional[CreateOnlineTeamsMeetingResponseJoinMeetingIdSettings]):
        join_url (Optional[str]): The web address used to join the Teams meeting. Example:
                https://teams.microsoft.com/l/meetup-join/19%3ameeting_NzM1NmIyZmMtMTdmNy00ZTUwLThmNzUtNzEzMmQ4YjlkNTU4%40thread
                .v2/0?context=%7b%22Tid%22%3a%222999126d-261b-4dfd-a3fb-65e7cd9a4db0%22%2c%22Oid%22%3a%2211847e94-4927-4a2d-
                8a48-c4658959d883%22%7d.
        join_web_url (Optional[str]): The URL to join the Teams meeting via a web browser. Example:
                https://teams.microsoft.com/l/meetup-join/19%3ameeting_NzM1NmIyZmMtMTdmNy00ZTUwLThmNzUtNzEzMmQ4YjlkNTU4%40thread
                .v2/0?context=%7b%22Tid%22%3a%222999126d-261b-4dfd-a3fb-65e7cd9a4db0%22%2c%22Oid%22%3a%2211847e94-4927-4a2d-
                8a48-c4658959d883%22%7d.
        lobby_bypass_settings (Optional[CreateOnlineTeamsMeetingResponseLobbyBypassSettings]):
        meeting_code (Optional[str]): A unique code used to access the meeting. Example: 231045254323.
        participants (Optional[CreateOnlineTeamsMeetingResponseParticipants]):
        record_automatically (Optional[bool]): Indicates whether to record the meeting automatically Example: True.
        share_meeting_chat_history_default (Optional[str]): Indicates if the meeting chat history is shared by default.
                Example: none.
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
    allow_meeting_chat: Optional["CreateOnlineTeamsMeetingResponseAllowMeetingChat"] = (
        Field(alias="allowMeetingChat", default=None)
    )
    allow_participants_to_change_name: Optional[bool] = Field(
        alias="allowParticipantsToChangeName", default=None
    )
    allow_recording: Optional[bool] = Field(alias="allowRecording", default=None)
    allow_teamwork_reactions: Optional[bool] = Field(
        alias="allowTeamworkReactions", default=None
    )
    allow_transcription: Optional[bool] = Field(
        alias="allowTranscription", default=None
    )
    allowed_presenters: Optional[
        "CreateOnlineTeamsMeetingResponseAllowedPresenters"
    ] = Field(alias="allowedPresenters", default=None)
    auto_admitted_users: Optional[str] = Field(alias="autoAdmittedUsers", default=None)
    chat_info: Optional["CreateOnlineTeamsMeetingResponseChatInfo"] = Field(
        alias="chatInfo", default=None
    )
    creation_date_time: Optional[datetime.datetime] = Field(
        alias="creationDateTime", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    is_broadcast: Optional[bool] = Field(alias="isBroadcast", default=None)
    is_entry_exit_announced: Optional[bool] = Field(
        alias="isEntryExitAnnounced", default=None
    )
    join_information: Optional["CreateOnlineTeamsMeetingResponseJoinInformation"] = (
        Field(alias="joinInformation", default=None)
    )
    join_meeting_id_settings: Optional[
        "CreateOnlineTeamsMeetingResponseJoinMeetingIdSettings"
    ] = Field(alias="joinMeetingIdSettings", default=None)
    join_url: Optional[str] = Field(alias="joinUrl", default=None)
    join_web_url: Optional[str] = Field(alias="joinWebUrl", default=None)
    lobby_bypass_settings: Optional[
        "CreateOnlineTeamsMeetingResponseLobbyBypassSettings"
    ] = Field(alias="lobbyBypassSettings", default=None)
    meeting_code: Optional[str] = Field(alias="meetingCode", default=None)
    participants: Optional["CreateOnlineTeamsMeetingResponseParticipants"] = Field(
        alias="participants", default=None
    )
    record_automatically: Optional[bool] = Field(
        alias="recordAutomatically", default=None
    )
    share_meeting_chat_history_default: Optional[str] = Field(
        alias="shareMeetingChatHistoryDefault", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateOnlineTeamsMeetingResponse"], src_dict: Dict[str, Any]
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

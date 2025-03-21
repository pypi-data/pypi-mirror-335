from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_all_transcripts_meeting_organizer import (
    ListAllTranscriptsMeetingOrganizer,
)
import datetime


class ListAllTranscripts(BaseModel):
    """
    Attributes:
        created_date_time (Optional[datetime.datetime]): The date and time when the transcript was created Example:
                2021-09-17T06:09:24.8968037Z.
        id (Optional[str]): The unique identifier for the meeting's transcript. Example:
                MSMjMCMjZDAwYWU3NjUtNmM2Yi00NjQxLTgwMWQtMTkzMmFmMjEzNzdh.
        meeting_id (Optional[str]): A unique identifier for the specific meeting. Example:
                MSo1N2Y5ZGFjYy03MWJmLTQ3NDMtYjQxMy01M2EdFGkdRWHJlQ.
        meeting_organizer (Optional[ListAllTranscriptsMeetingOrganizer]):
        transcript_content_url (Optional[str]): URL to download the transcript of the meeting Example: https://graph.mic
                rosoft.com/v1.0/$metadata#users('ba321e0d-79ee-478d-8e28-
                85a19507f456')/onlineMeetings('MSo1N2Y5ZGFjYy03MWJmLTQ3NDMtYjQxMy01M2EdFGkdRWHJlQ')/transcripts/('MSMjMCMjZDAwYW
                U3NjUtNmM2Yi00NjQxLTgwMWQtMTkzMmFmMjEzNzdh')/content.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    meeting_id: Optional[str] = Field(alias="meetingId", default=None)
    meeting_organizer: Optional["ListAllTranscriptsMeetingOrganizer"] = Field(
        alias="meetingOrganizer", default=None
    )
    transcript_content_url: Optional[str] = Field(
        alias="transcriptContentUrl", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListAllTranscripts"], src_dict: Dict[str, Any]):
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

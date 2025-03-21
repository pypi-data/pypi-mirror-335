from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class CreateOnlineTeamsMeetingResponseJoinMeetingIdSettings(BaseModel):
    """
    Attributes:
        is_passcode_required (Optional[bool]): Indicates whether a passcode is required to join a meeting when using
                Join Meeting ID Example: True.
        join_meeting_id (Optional[str]): A unique identifier to join the meeting. Example: 231045254323.
        passcode (Optional[str]): The passcode required for joining the meeting Example: mKBhMi.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    is_passcode_required: Optional[bool] = Field(
        alias="isPasscodeRequired", default=None
    )
    join_meeting_id: Optional[str] = Field(alias="joinMeetingId", default=None)
    passcode: Optional[str] = Field(alias="passcode", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateOnlineTeamsMeetingResponseJoinMeetingIdSettings"],
        src_dict: Dict[str, Any],
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

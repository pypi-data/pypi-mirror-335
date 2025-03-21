from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.getonline_meetings_response_participants_attendees_identity import (
    GetonlineMeetingsResponseParticipantsAttendeesIdentity,
)


class GetonlineMeetingsResponseParticipantsAttendeesArrayItemRef(BaseModel):
    """
    Attributes:
        identity (Optional[GetonlineMeetingsResponseParticipantsAttendeesIdentity]):
        role (Optional[str]): The role assigned to each meeting attendee. Example: attendee.
        upn (Optional[str]): The User Principal Names (UPNs) of the meeting attendees. Example:
                mukesh.kumar_uipath.com#EXT#@uipathsandboxes.onmicrosoft.com.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    identity: Optional["GetonlineMeetingsResponseParticipantsAttendeesIdentity"] = (
        Field(alias="identity", default=None)
    )
    role: Optional[str] = Field(alias="role", default=None)
    upn: Optional[str] = Field(alias="upn", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetonlineMeetingsResponseParticipantsAttendeesArrayItemRef"],
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

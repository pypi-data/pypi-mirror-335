from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class ListAllTranscriptsMeetingOrganizerUser(BaseModel):
    """
    Attributes:
        id (Optional[str]): Unique ID for the user organizing the meeting Example: ba321e0d-79ee-478d-8e28-85a19507f456.
        tenant_id (Optional[str]): Unique ID for the organizer's Office 365 tenant Example:
                cd6cee19-2d76-4ee0-8f47-9ed12ee44331.
        user_identity_type (Optional[str]): Type of identity used by the meeting organizer Example: aadUser.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    tenant_id: Optional[str] = Field(alias="tenantId", default=None)
    user_identity_type: Optional[str] = Field(alias="userIdentityType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["ListAllTranscriptsMeetingOrganizerUser"], src_dict: Dict[str, Any]
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

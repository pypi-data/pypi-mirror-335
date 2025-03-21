from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetonlineMeetingsResponseParticipantsAttendeesIdentityUser(BaseModel):
    """
    Attributes:
        id (Optional[str]): Unique identifier for each meeting attendee. Example: 4138edd3-f7b7-4db0-9044-733468597ad7.
        identity_provider (Optional[str]): The service that verifies each attendee's identity. Example: AAD.
        tenant_id (Optional[str]): The unique identifier of the attendee's organization. Example:
                2999126d-261b-4dfd-a3fb-65e7cd9a4db0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: Optional[str] = Field(alias="id", default=None)
    identity_provider: Optional[str] = Field(alias="identityProvider", default=None)
    tenant_id: Optional[str] = Field(alias="tenantId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetonlineMeetingsResponseParticipantsAttendeesIdentityUser"],
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class SendChannelMessageRequestMentionsMentionedUser(BaseModel):
    """
    Attributes:
        display_name (Optional[str]):  Example: Prakash Buthukuri.
        id (Optional[str]):  Example: e02b1739-a50b-4eb6-acd4-c52fd942b27f.
        user_identity_type (Optional[str]):  Example: aadUser.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    display_name: Optional[str] = Field(alias="displayName", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    user_identity_type: Optional[str] = Field(alias="userIdentityType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SendChannelMessageRequestMentionsMentionedUser"],
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

from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class ListChannelMessagesRepliesFromUser(BaseModel):
    """
    Attributes:
        display_name (Optional[str]):  Example: UiPath Developer.
        id (Optional[str]):  Example: f7ef94d2-c232-4bf8-a216-ff591ad0dd3a.
        tenant_id (Optional[str]):  Example: 2999126d-261b-4dfd-a3fb-65e7cd9a4db0.
        user_identity_type (Optional[str]):  Example: aadUser.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    display_name: Optional[str] = Field(alias="displayName", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    tenant_id: Optional[str] = Field(alias="tenantId", default=None)
    user_identity_type: Optional[str] = Field(alias="userIdentityType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["ListChannelMessagesRepliesFromUser"], src_dict: Dict[str, Any]
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

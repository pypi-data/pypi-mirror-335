from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class CreateOneOnOneChatResponse(BaseModel):
    """
    Attributes:
        chat_type (Optional[str]):  Example: oneOnOne.
        created_date_time (Optional[datetime.datetime]):  Example: 2022-07-27T06:15:58.688Z.
        id (Optional[str]): ID of the new Chat. Example:
                19:4aa1ebc2-1501-4f0b-9c8c-5746a2c55079_cb31e410-1a0f-485c-9406-bed77a87a8b5@unq.gbl.spaces.
        last_updated_date_time (Optional[datetime.datetime]):  Example: 2022-07-27T06:15:58.688Z.
        odata_context (Optional[str]):  Example: https://graph.microsoft.com/v1.0/$metadata#chats/$entity.
        tenant_id (Optional[str]):  Example: 42803ef2-75b8-4aba-910a-32c7df4e4b26.
        web_url (Optional[str]):  Example: https://teams.microsoft.com/l/chat/19%3A4aa1ebc2-1501-4f0b-9c8c-
                5746a2c55079_cb31e410-1a0f-485c-9406-bed77a87a8b5%40unq.gbl.spaces/0?tenantId=42803ef2-75b8-4aba-910a-
                32c7df4e4b26.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    chat_type: Optional[str] = Field(alias="chatType", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    last_updated_date_time: Optional[datetime.datetime] = Field(
        alias="lastUpdatedDateTime", default=None
    )
    odata_context: Optional[str] = Field(alias="odataContext", default=None)
    tenant_id: Optional[str] = Field(alias="tenantId", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateOneOnOneChatResponse"], src_dict: Dict[str, Any]):
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

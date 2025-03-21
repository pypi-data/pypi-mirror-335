from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_chat_messages_body import ListChatMessagesBody
from ..models.list_chat_messages_from import ListChatMessagesFrom
from ..models.list_chat_messages_mentions_array_item_ref import (
    ListChatMessagesMentionsArrayItemRef,
)
import datetime


class ListChatMessages(BaseModel):
    """
    Attributes:
        body (Optional[ListChatMessagesBody]):
        chat_id (Optional[str]):  Example:
                19:89a3e0f6-9cb8-4515-9a8b-9d9811e1a2bd_f7ef94d2-c232-4bf8-a216-ff591ad0dd3a@unq.gbl.spaces.
        created_date_time (Optional[datetime.datetime]):  Example: 2023-10-05T18:31:42.557Z.
        etag (Optional[str]):  Example: 1696530702557.
        from_ (Optional[ListChatMessagesFrom]):
        id (Optional[str]):  Example: 1696530702557.
        importance (Optional[str]):  Example: normal.
        last_modified_date_time (Optional[datetime.datetime]):  Example: 2023-10-05T18:31:42.557Z.
        locale (Optional[str]):  Example: en-us.
        mentions (Optional[list['ListChatMessagesMentionsArrayItemRef']]):
        message_type (Optional[str]):  Example: message.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: Optional["ListChatMessagesBody"] = Field(alias="body", default=None)
    chat_id: Optional[str] = Field(alias="chatId", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    etag: Optional[str] = Field(alias="etag", default=None)
    from_: Optional["ListChatMessagesFrom"] = Field(alias="from", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[str] = Field(alias="importance", default=None)
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    locale: Optional[str] = Field(alias="locale", default=None)
    mentions: Optional[list["ListChatMessagesMentionsArrayItemRef"]] = Field(
        alias="mentions", default=None
    )
    message_type: Optional[str] = Field(alias="messageType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListChatMessages"], src_dict: Dict[str, Any]):
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

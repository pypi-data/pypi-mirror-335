from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_channel_messages_attachments_array_item_ref import (
    ListChannelMessagesAttachmentsArrayItemRef,
)
from ..models.list_channel_messages_body import ListChannelMessagesBody
from ..models.list_channel_messages_channel_identity import (
    ListChannelMessagesChannelIdentity,
)
from ..models.list_channel_messages_from import ListChannelMessagesFrom
from ..models.list_channel_messages_replies_array_item_ref import (
    ListChannelMessagesRepliesArrayItemRef,
)
import datetime


class ListChannelMessages(BaseModel):
    """
    Attributes:
        attachments (Optional[list['ListChannelMessagesAttachmentsArrayItemRef']]):
        body (Optional[ListChannelMessagesBody]):
        channel_identity (Optional[ListChannelMessagesChannelIdentity]):
        created_date_time (Optional[datetime.datetime]):  Example: 2023-10-30T11:25:40.375Z.
        etag (Optional[str]):  Example: 1698665140375.
        from_ (Optional[ListChannelMessagesFrom]):
        id (Optional[str]):  Example: 1698665140375.
        importance (Optional[str]):  Example: normal.
        last_modified_date_time (Optional[datetime.datetime]):  Example: 2023-10-30T11:25:40.375Z.
        locale (Optional[str]):  Example: en-us.
        message_type (Optional[str]):  Example: message.
        replies (Optional[list['ListChannelMessagesRepliesArrayItemRef']]):
        web_url (Optional[str]):  Example: https://teams.microsoft.com/l/message/19%3A00d04403803d43189eab1812fcbcabb7%4
                0thread.tacv2/1698665140375?groupId=ffa073be-5e77-448b-bbad-68be276c0876&tenantId=2999126d-261b-4dfd-a3fb-
                65e7cd9a4db0&createdTime=1698665140375&parentMessageId=1698665140375.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    attachments: Optional[list["ListChannelMessagesAttachmentsArrayItemRef"]] = Field(
        alias="attachments", default=None
    )
    body: Optional["ListChannelMessagesBody"] = Field(alias="body", default=None)
    channel_identity: Optional["ListChannelMessagesChannelIdentity"] = Field(
        alias="channelIdentity", default=None
    )
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    etag: Optional[str] = Field(alias="etag", default=None)
    from_: Optional["ListChannelMessagesFrom"] = Field(alias="from", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[str] = Field(alias="importance", default=None)
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    locale: Optional[str] = Field(alias="locale", default=None)
    message_type: Optional[str] = Field(alias="messageType", default=None)
    replies: Optional[list["ListChannelMessagesRepliesArrayItemRef"]] = Field(
        alias="replies", default=None
    )
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListChannelMessages"], src_dict: Dict[str, Any]):
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

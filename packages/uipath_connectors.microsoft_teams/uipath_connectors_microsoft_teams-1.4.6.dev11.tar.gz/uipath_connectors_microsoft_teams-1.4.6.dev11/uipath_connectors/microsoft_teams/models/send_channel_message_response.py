from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_channel_message_response_body import SendChannelMessageResponseBody
from ..models.send_channel_message_response_channel_identity import (
    SendChannelMessageResponseChannelIdentity,
)
from ..models.send_channel_message_response_from import SendChannelMessageResponseFrom
from ..models.send_channel_message_response_mentions import (
    SendChannelMessageResponseMentions,
)
import datetime


class SendChannelMessageResponse(BaseModel):
    """
    Attributes:
        body (Optional[SendChannelMessageResponseBody]):
        channel_identity (Optional[SendChannelMessageResponseChannelIdentity]):
        created_date_time (Optional[datetime.datetime]):  Example: 2022-08-08T17:52:39.221Z.
        etag (Optional[str]):  Example: 1659981159221.
        from_ (Optional[SendChannelMessageResponseFrom]):
        id (Optional[str]): The ID of the message to send reply to in teams. The ID of the message can be retrieved from
                the output parameter 'ID' of the Send Channel Message or Send Chat Message activity Example: 1659981159221.
        importance (Optional[str]):  Example: normal.
        last_modified_date_time (Optional[datetime.datetime]):  Example: 2022-08-08T17:52:39.221Z.
        locale (Optional[str]):  Example: en-us.
        mentions (Optional[SendChannelMessageResponseMentions]):
        message_type (Optional[str]):  Example: message.
        odata_context (Optional[str]):  Example: https://graph.microsoft.com/v1.0/$metadata#teams('72b491a2-ab4b-4528-
                9a18-0844f037f33b')/channels('19%3A646a8f3aab7d49bfb4d894bd6513ba5d%40thread.tacv2')/messages/$entity.
        web_url (Optional[str]): Web URL Example: https://teams.microsoft.com/l/message/19%3A646a8f3aab7d49bfb4d894bd651
                3ba5d%40thread.tacv2/1659981159221?groupId=72b491a2-ab4b-4528-9a18-0844f037f33b&tenantId=42803ef2-75b8-4aba-
                910a-32c7df4e4b26&createdTime=1659981159221&parentMessageId=1659981159221.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: Optional["SendChannelMessageResponseBody"] = Field(alias="body", default=None)
    channel_identity: Optional["SendChannelMessageResponseChannelIdentity"] = Field(
        alias="channelIdentity", default=None
    )
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    etag: Optional[str] = Field(alias="etag", default=None)
    from_: Optional["SendChannelMessageResponseFrom"] = Field(
        alias="from", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[str] = Field(alias="importance", default=None)
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    locale: Optional[str] = Field(alias="locale", default=None)
    mentions: Optional["SendChannelMessageResponseMentions"] = Field(
        alias="mentions", default=None
    )
    message_type: Optional[str] = Field(alias="messageType", default=None)
    odata_context: Optional[str] = Field(alias="odataContext", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendChannelMessageResponse"], src_dict: Dict[str, Any]):
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

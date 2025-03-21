from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_chat_message_response_body import SendChatMessageResponseBody
from ..models.send_chat_message_response_from import SendChatMessageResponseFrom
from ..models.send_chat_message_response_mentions import SendChatMessageResponseMentions
import datetime


class SendChatMessageResponse(BaseModel):
    """
    Attributes:
        body (Optional[SendChatMessageResponseBody]):
        chat_id (Optional[str]):  Example: 19:960bc071dfb740208a73a503881817f8@thread.v2.
        created_date_time (Optional[datetime.datetime]):  Example: 2022-08-08T17:58:36.302Z.
        etag (Optional[str]):  Example: 1659981516302.
        from_ (Optional[SendChatMessageResponseFrom]):
        id (Optional[str]): The ID of the message to send reply to in teams. The ID of the message can be retrieved from
                the output parameter 'ID' of the Send Channel Message or Send Chat Message activity Example: 1659981516302.
        importance (Optional[str]):  Example: normal.
        last_modified_date_time (Optional[datetime.datetime]):  Example: 2022-08-08T17:58:36.302Z.
        locale (Optional[str]):  Example: en-us.
        mentions (Optional[SendChatMessageResponseMentions]):
        message_type (Optional[str]):  Example: message.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: Optional["SendChatMessageResponseBody"] = Field(alias="body", default=None)
    chat_id: Optional[str] = Field(alias="chatId", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    etag: Optional[str] = Field(alias="etag", default=None)
    from_: Optional["SendChatMessageResponseFrom"] = Field(alias="from", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[str] = Field(alias="importance", default=None)
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    locale: Optional[str] = Field(alias="locale", default=None)
    mentions: Optional["SendChatMessageResponseMentions"] = Field(
        alias="mentions", default=None
    )
    message_type: Optional[str] = Field(alias="messageType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendChatMessageResponse"], src_dict: Dict[str, Any]):
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

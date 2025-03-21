from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_individual_chat_message_response_body import (
    CreateIndividualChatMessageResponseBody,
)
from ..models.create_individual_chat_message_response_from import (
    CreateIndividualChatMessageResponseFrom,
)
import datetime


class CreateIndividualChatMessageResponse(BaseModel):
    """
    Attributes:
        chat_id (str): Enter a private chat ID to send a message to a specific chat. You can pass "48:notes" to send
                message to yourself. Note: "48:notes" is not officially documented by Microsoft and may change in future.
                Example: 19:f2db4e0b-b680-484a-9e05-1095511cb383_f7ef94d2-c232-4bf8-a216-ff591ad0dd3a@unq.gbl.spaces.
        body (Optional[CreateIndividualChatMessageResponseBody]):
        created_date_time (Optional[datetime.datetime]):  Example: 2023-10-17T19:16:45.969Z.
        etag (Optional[str]):  Example: 1697570205969.
        from_ (Optional[CreateIndividualChatMessageResponseFrom]):
        id (Optional[str]):  Example: 1697570205969.
        importance (Optional[str]):  Example: normal.
        last_modified_date_time (Optional[datetime.datetime]):  Example: 2023-10-17T19:16:45.969Z.
        locale (Optional[str]):  Example: en-us.
        message_type (Optional[str]): The content of the message to be sent Example: message.
        odata_context (Optional[str]):  Example: https://graph.microsoft.com/v1.0/$metadata#chats('19%3Af2db4e0b-b680-
                484a-9e05-1095511cb383_f7ef94d2-c232-4bf8-a216-ff591ad0dd3a%40unq.gbl.spaces')/messages/$entity.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    chat_id: str = Field(alias="chatId")
    body: Optional["CreateIndividualChatMessageResponseBody"] = Field(
        alias="body", default=None
    )
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    etag: Optional[str] = Field(alias="etag", default=None)
    from_: Optional["CreateIndividualChatMessageResponseFrom"] = Field(
        alias="from", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[str] = Field(alias="importance", default=None)
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    locale: Optional[str] = Field(alias="locale", default=None)
    message_type: Optional[str] = Field(alias="messageType", default=None)
    odata_context: Optional[str] = Field(alias="odataContext", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateIndividualChatMessageResponse"], src_dict: Dict[str, Any]
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

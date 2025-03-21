from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_individual_chat_message_request_body import (
    CreateIndividualChatMessageRequestBody,
)
from ..models.create_individual_chat_message_request_mentions import (
    CreateIndividualChatMessageRequestMentions,
)
from ..models.create_individual_chat_message_request_message_using import (
    CreateIndividualChatMessageRequestMessageUsing,
)
from ..models.create_individual_chat_message_request_roles import (
    CreateIndividualChatMessageRequestRoles,
)


class CreateIndividualChatMessageRequest(BaseModel):
    """
    Attributes:
        chat_id (str): Enter a private chat ID to send a message to a specific chat. You can pass "48:notes" to send
                message to yourself. Note: "48:notes" is not officially documented by Microsoft and may change in future.
                Example: 19:f2db4e0b-b680-484a-9e05-1095511cb383_f7ef94d2-c232-4bf8-a216-ff591ad0dd3a@unq.gbl.spaces.
        message_using (CreateIndividualChatMessageRequestMessageUsing): Whether to send the message using email address
                (UPN) or chat ID? Example: email.
        roles (CreateIndividualChatMessageRequestRoles): The role of the user which can be ‘Owner’ or ‘Guest’. “Owner”
                is a team admin that can manage the team and its members while “Guest” is a person invited from outside of your
                organization. Default: CreateIndividualChatMessageRequestRoles.OWNER. Example: guest.
        user_email (str): Type the user principal name (UPN), i.e. user email address. This should be the unique user
                login to Azure AD and other Office services. Example: raman.keshamoni@uipath.com.
        attachment_ids (Optional[list[str]]):
        body (Optional[CreateIndividualChatMessageRequestBody]):
        mentions (Optional[CreateIndividualChatMessageRequestMentions]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    chat_id: str = Field(alias="chatId")
    message_using: "CreateIndividualChatMessageRequestMessageUsing" = Field(
        alias="messageUsing"
    )
    user_email: str = Field(alias="userEmail")
    roles: "CreateIndividualChatMessageRequestRoles" = Field(
        alias="roles", default=CreateIndividualChatMessageRequestRoles.OWNER
    )
    attachment_ids: Optional[list[str]] = Field(alias="attachmentIds", default=None)
    body: Optional["CreateIndividualChatMessageRequestBody"] = Field(
        alias="body", default=None
    )
    mentions: Optional["CreateIndividualChatMessageRequestMentions"] = Field(
        alias="mentions", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateIndividualChatMessageRequest"], src_dict: Dict[str, Any]
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

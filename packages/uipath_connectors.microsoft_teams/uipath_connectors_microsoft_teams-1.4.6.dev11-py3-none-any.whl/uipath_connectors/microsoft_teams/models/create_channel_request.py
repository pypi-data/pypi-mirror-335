from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_channel_request_members_array_item_ref import (
    CreateChannelRequestMembersArrayItemRef,
)
from ..models.create_channel_request_membership_type import (
    CreateChannelRequestMembershipType,
)


class CreateChannelRequest(BaseModel):
    """
    Attributes:
        display_name (str): The display name of the new channel Example: My First  Channel 1.
        membership_type (CreateChannelRequestMembershipType): The type of channel being created. Use 'Standard' for
                sharing the channel with all team members, 'Private' for sharing the channel with selected team members and
                'Shared' for sharing the channel with people both inside and outside the team Example: Standard.
        description (Optional[str]): The description of the channel Example: This is my first private channels 1.
        members (Optional[list['CreateChannelRequestMembersArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    display_name: str = Field(alias="displayName")
    membership_type: "CreateChannelRequestMembershipType" = Field(
        alias="membershipType"
    )
    description: Optional[str] = Field(alias="description", default=None)
    members: Optional[list["CreateChannelRequestMembersArrayItemRef"]] = Field(
        alias="members", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateChannelRequest"], src_dict: Dict[str, Any]):
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

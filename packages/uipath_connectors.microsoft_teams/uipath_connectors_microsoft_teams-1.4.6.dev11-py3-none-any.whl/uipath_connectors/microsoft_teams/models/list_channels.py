from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_channels_membership_type import ListChannelsMembershipType
import datetime


class ListChannels(BaseModel):
    """
    Attributes:
        created_date_time (Optional[datetime.datetime]):  Example: 2022-07-27T15:41:31.891Z.
        description (Optional[str]): The description of the channel Example: This is my first private channels 1.
        display_name (Optional[str]): The display name of the new channel Example: My First  Channel 1.
        email (Optional[str]):  Example: FirstSingle@Uipath689.onmicrosoft.com.
        id (Optional[str]): ID of the new channel Example: 19:646a8f3aab7d49bfb4d894bd6513ba5d@thread.tacv2.
        membership_type (Optional[ListChannelsMembershipType]): The type of channel being created. Use 'Standard' for
                sharing the channel with all team members, 'Private' for sharing the channel with selected team members and
                'Shared' for sharing the channel with people both inside and outside the team Example: Standard.
        tenant_id (Optional[str]):  Example: 42803ef2-75b8-4aba-910a-32c7df4e4b26.
        web_url (Optional[str]):  Example: https://teams.microsoft.com/l/channel/19%3A646a8f3aab7d49bfb4d894bd6513ba5d%4
                0thread.tacv2/My%20First%20%20Channel%201?groupId=72b491a2-ab4b-4528-9a18-0844f037f33b&tenantId=42803ef2-75b8-
                4aba-910a-32c7df4e4b26&allowXTenantAccess=False.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    description: Optional[str] = Field(alias="description", default=None)
    display_name: Optional[str] = Field(alias="displayName", default=None)
    email: Optional[str] = Field(alias="email", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    membership_type: Optional["ListChannelsMembershipType"] = Field(
        alias="membershipType", default=None
    )
    tenant_id: Optional[str] = Field(alias="tenantId", default=None)
    web_url: Optional[str] = Field(alias="webUrl", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListChannels"], src_dict: Dict[str, Any]):
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

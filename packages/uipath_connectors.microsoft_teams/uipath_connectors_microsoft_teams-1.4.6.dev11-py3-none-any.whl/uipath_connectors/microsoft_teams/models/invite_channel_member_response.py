from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.invite_channel_member_response_roles import (
    InviteChannelMemberResponseRoles,
)
import datetime


class InviteChannelMemberResponse(BaseModel):
    """
    Attributes:
        email (str): Type the user principal name (UPN) i.e. user email address. This should be the unique user login to
                Azure AD and other Office services. In very rare cases, UPN could be set to something else by Azure AD admin
                Example: prakash@Uipath689.onmicrosoft.com.
        display_name (Optional[str]):  Example: Prakash Buthukuri.
        id (Optional[str]): ID of the new member in the channel. Example: MCMjMiMjNDI4MDNlZjItNzViOC00YWJhLTkxMGEtMzJjN2
                RmNGU0YjI2IyMxOTphYTU3OWU2M2UwMGU0MmYxYmVlZTVjMzc1YTYxMzJjNEB0aHJlYWQudGFjdjIjI2UwMmIxNzM5LWE1MGItNGViNi1hY2Q0LW
                M1MmZkOTQyYjI3Zg==.
        odata_context (Optional[str]):  Example: https://graph.microsoft.com/v1.0/$metadata#teams('72b491a2-ab4b-4528-
                9a18-0844f037f33b')/channels('19%3Aaa579e63e00e42f1beee5c375a6132c4%40thread.tacv2')/members/$entity.
        odata_type (Optional[str]):  Example: #microsoft.graph.aadUserConversationMember.
        roles (Optional[InviteChannelMemberResponseRoles]): The role of the user which can be 'Owner' or 'Guest'.
                'Owner' is a channel admin that can manage the channel and its members while 'Guest' is a person invited from
                outside of your organization. For normal team members, no role is required Example: owner.
        tenant_id (Optional[str]):  Example: 42803ef2-75b8-4aba-910a-32c7df4e4b26.
        user_id (Optional[str]):  Example: e02b1739-a50b-4eb6-acd4-c52fd942b27f.
        visible_history_start_date_time (Optional[datetime.datetime]):  Example: 0001-01-01T00:00:00Z.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    email: str = Field(alias="email")
    display_name: Optional[str] = Field(alias="displayName", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    odata_context: Optional[str] = Field(alias="odataContext", default=None)
    odata_type: Optional[str] = Field(alias="odataType", default=None)
    roles: Optional["InviteChannelMemberResponseRoles"] = Field(
        alias="roles", default=None
    )
    tenant_id: Optional[str] = Field(alias="tenantId", default=None)
    user_id: Optional[str] = Field(alias="userId", default=None)
    visible_history_start_date_time: Optional[datetime.datetime] = Field(
        alias="visibleHistoryStartDateTime", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["InviteChannelMemberResponse"], src_dict: Dict[str, Any]):
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

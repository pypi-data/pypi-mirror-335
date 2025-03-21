from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.invite_team_member_response_roles import InviteTeamMemberResponseRoles
import datetime


class InviteTeamMemberResponse(BaseModel):
    """
    Attributes:
        roles (InviteTeamMemberResponseRoles): The role of the user which can be ‘Owner’ or ‘Guest’. “Owner” is a
                channel admin that can manage the channel and its members while “Guest” is a person invited from outside of your
                organization Default: InviteTeamMemberResponseRoles.OWNER. Example: owner.
        user_id (str): Type the user email address i.e. user principal name (UPN) Example:
                onedrive@uipathsandboxes.onmicrosoft.com.
        display_name (Optional[str]):  Example: onedrive test.
        email (Optional[str]): Type the user principal name (UPN) i.e. user email address. This should be the unique
                user login to Azure AD and other Office services. In very rare cases, UPN could be set to something else by
                Azure AD admin Example: onedrive@uipathsandboxes.onmicrosoft.com.
        id (Optional[str]):  Example: MCMjMSMjMjk5OTEyNmQtMjYxYi00ZGZkLWEzZmItNjVlN2NkOWE0ZGIwIyNmZmEwNzNiZS01ZTc3LTQ0OG
                ItYmJhZC02OGJlMjc2YzA4NzYjIzg5YTNlMGY2LTljYjgtNDUxNS05YThiLTlkOTgxMWUxYTJiZA==.
        odata_context (Optional[str]):  Example:
                https://graph.microsoft.com/v1.0/$metadata#teams('ffa073be-5e77-448b-bbad-68be276c0876')/members/$entity.
        odata_type (Optional[str]):  Example: #microsoft.graph.aadUserConversationMember.
        tenant_id (Optional[str]):  Example: 2999126d-261b-4dfd-a3fb-65e7cd9a4db0.
        visible_history_start_date_time (Optional[datetime.datetime]):  Example: 0001-01-01T00:00:00Z.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    user_id: str = Field(alias="userId")
    roles: "InviteTeamMemberResponseRoles" = Field(
        alias="roles", default=InviteTeamMemberResponseRoles.OWNER
    )
    display_name: Optional[str] = Field(alias="displayName", default=None)
    email: Optional[str] = Field(alias="email", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    odata_context: Optional[str] = Field(alias="odataContext", default=None)
    odata_type: Optional[str] = Field(alias="odataType", default=None)
    tenant_id: Optional[str] = Field(alias="tenantId", default=None)
    visible_history_start_date_time: Optional[datetime.datetime] = Field(
        alias="visibleHistoryStartDateTime", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["InviteTeamMemberResponse"], src_dict: Dict[str, Any]):
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

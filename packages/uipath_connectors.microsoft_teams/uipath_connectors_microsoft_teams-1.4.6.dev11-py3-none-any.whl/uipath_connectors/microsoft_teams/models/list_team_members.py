from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class ListTeamMembers(BaseModel):
    """
    Attributes:
        display_name (Optional[str]):  Example: Rakesh Mahto.
        email (Optional[str]):  Example: developer@uipathsandboxes.onmicrosoft.com.
        id (Optional[str]):  Example: MCMjMSMjMjk5OTEyNmQtMjYxYi00ZGZkLWEzZmItNjVlN2NkOWE0ZGIwIyNmZmEwNzNiZS01ZTc3LTQ0OG
                ItYmJhZC02OGJlMjc2YzA4NzYjIzExODQ3ZTk0LTQ5MjctNGEyZC04YTQ4LWM0NjU4OTU5ZDg4Mw==.
        odata_type (Optional[str]):  Example: #microsoft.graph.aadUserConversationMember.
        roles (Optional[str]):
        tenant_id (Optional[str]):  Example: 2999126d-261b-4dfd-a3fb-65e7cd9a4db0.
        user_id (Optional[str]):  Example: 11847e94-4927-4a2d-8a48-c4658959d883.
        visible_history_start_date_time (Optional[datetime.datetime]):  Example: 0001-01-01T00:00:00Z.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    display_name: Optional[str] = Field(alias="displayName", default=None)
    email: Optional[str] = Field(alias="email", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    odata_type: Optional[str] = Field(alias="odataType", default=None)
    roles: Optional[str] = Field(alias="roles", default=None)
    tenant_id: Optional[str] = Field(alias="tenantId", default=None)
    user_id: Optional[str] = Field(alias="userId", default=None)
    visible_history_start_date_time: Optional[datetime.datetime] = Field(
        alias="visibleHistoryStartDateTime", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListTeamMembers"], src_dict: Dict[str, Any]):
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

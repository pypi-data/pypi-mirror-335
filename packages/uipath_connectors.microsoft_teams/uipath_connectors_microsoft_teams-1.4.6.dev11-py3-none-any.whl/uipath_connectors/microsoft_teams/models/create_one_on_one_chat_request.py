from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Type

from ..models.create_one_on_one_chat_request_roles import CreateOneOnOneChatRequestRoles


class CreateOneOnOneChatRequest(BaseModel):
    """
    Attributes:
        roles (CreateOneOnOneChatRequestRoles): The role of the user which can be 'Owner' or 'Guest'. 'Owner' is a
                channel admin that can manage the channel and its members while 'Guest' is a person invited from outside of your
                organization. For normal team members, no role is required Default: CreateOneOnOneChatRequestRoles.OWNER.
                Example: owner.
        user_email (str): Type the user principal name (UPN) i.e. user email address. This should be the unique user
                login to Azure AD and other Office services. In very rare cases, UPN could be set to something else by Azure AD
                admin Example: rakesh@Uipath689.onmicrosoft.com.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    user_email: str = Field(alias="userEmail")
    roles: "CreateOneOnOneChatRequestRoles" = Field(
        alias="roles", default=CreateOneOnOneChatRequestRoles.OWNER
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateOneOnOneChatRequest"], src_dict: Dict[str, Any]):
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

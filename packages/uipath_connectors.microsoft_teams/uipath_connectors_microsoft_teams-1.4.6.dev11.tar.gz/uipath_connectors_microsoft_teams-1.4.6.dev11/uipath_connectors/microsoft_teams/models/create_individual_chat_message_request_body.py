from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class CreateIndividualChatMessageRequestBody(BaseModel):
    r"""
    Attributes:
        adaptive_card_content (Optional[str]): Pass the string by converting the generated JSON from
                https://adaptivecards.io/designer/. Replace \" with ' and remove all the escape characters having '\' such as
                \n, \r as these are not supported. Ex: Replace \r\n\"type\" with 'type'
        content (Optional[str]):  Example: Hello.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    adaptive_card_content: Optional[str] = Field(
        alias="adaptiveCardContent", default=None
    )
    content: Optional[str] = Field(alias="content", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreateIndividualChatMessageRequestBody"], src_dict: Dict[str, Any]
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

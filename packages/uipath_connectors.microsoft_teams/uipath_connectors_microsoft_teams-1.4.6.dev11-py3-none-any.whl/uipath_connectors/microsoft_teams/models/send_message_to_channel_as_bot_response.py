from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class SendMessageToChannelAsBotResponse(BaseModel):
    """
    Attributes:
        activity_id (Optional[str]): A unique identifier for the specific message activity. Example: 1723528755774.
        id (Optional[str]): A unique identifier for the message being sent or received. Example:
                19:jlGsH6rOSZo8qJWpM2r8p7XaNiAjh5A-u2Q6jnbOSqI1@thread.tacv2;messageid=1723528755774.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    activity_id: Optional[str] = Field(alias="activityId", default=None)
    id: Optional[str] = Field(alias="id", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SendMessageToChannelAsBotResponse"], src_dict: Dict[str, Any]
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

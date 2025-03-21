import json
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_channel_message_request import SendChannelMessageRequest
from ..types import File, FileJsonType


class SendChannelMessageBody(BaseModel):
    """
    Attributes:
        body (SendChannelMessageRequest):
        file (Optional[File]): Image attachment to be uploaded
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: "SendChannelMessageRequest" = Field(alias="body")
    file: Optional[File] = Field(alias="file", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendChannelMessageBody"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    def to_multipart(self) -> dict[str, Any]:
        body = (None, json.dumps(self.body.to_dict()).encode(), "application/json")

        file: Optional[FileJsonType] = None
        if self.file is not None:
            file = self.file.to_tuple()

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_keys:
            field_dict[prop_name] = (
                None,
                str(self.__getitem__(prop)).encode(),
                "text/plain",
            )
        field_dict.update(
            {
                "body": body,
            }
        )
        if file is not None:
            field_dict["file"] = file

        return field_dict

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

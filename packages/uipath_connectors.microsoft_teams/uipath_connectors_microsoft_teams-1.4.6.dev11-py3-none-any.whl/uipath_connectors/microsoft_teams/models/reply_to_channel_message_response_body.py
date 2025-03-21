from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class ReplyToChannelMessageResponseBody(BaseModel):
    """
    Attributes:
        content (Optional[str]): The content of the message to be sent Example: Hi <at id="0">Prakash Buthukuri</at>
                <p>Test file attachment</p> <div><div>
                <div><span><img height="297" src="https://graph.microsoft.com/v1.0/teams/72b491a2-ab4b-4528-9a18-
                0844f037f33b/channels/19:646a8f3aab7d49bfb4d894bd6513ba5d@thread.tacv2/messages/1659981159221/replies/1659981284
                670/hostedContents/aWQ9MC13dXMtZDUtOWZkYmY4ZTlmMjQ3M2E5OWI2ODdkMDc5ZTEyYzU1N2EsdHlwZT0xLHVybD1odHRwczovL3VzLWFwa
                S5hc20uc2t5cGUuY29tL3YxL29iamVjdHMvMC13dXMtZDUtOWZkYmY4ZTlmMjQ3M2E5OWI2ODdkMDc5ZTEyYzU1N2Evdmlld3MvaW1nbw==/$val
                ue" width="297" style="vertical-align:bottom; width:297px; height:297px"></span>

                </div>


                </div>
                </div><attachment id="efb345a4-d37d-4b3d-9443-20691d2cddc1"></attachment>.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content: Optional[str] = Field(alias="content", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["ReplyToChannelMessageResponseBody"], src_dict: Dict[str, Any]
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

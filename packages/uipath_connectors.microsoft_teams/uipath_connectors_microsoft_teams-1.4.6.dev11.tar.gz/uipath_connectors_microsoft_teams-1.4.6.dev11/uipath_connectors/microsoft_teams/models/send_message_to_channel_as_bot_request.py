from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_message_to_channel_as_bot_request_activity import (
    SendMessageToChannelAsBotRequestActivity,
)
from ..models.send_message_to_channel_as_bot_request_bot import (
    SendMessageToChannelAsBotRequestBot,
)
from ..models.send_message_to_channel_as_bot_request_channel_data import (
    SendMessageToChannelAsBotRequestChannelData,
)
from ..models.send_message_to_channel_as_bot_request_text_type import (
    SendMessageToChannelAsBotRequestTextType,
)


class SendMessageToChannelAsBotRequest(BaseModel):
    """
    Attributes:
        channel_data (Optional[SendMessageToChannelAsBotRequestChannelData]):
        text_type (SendMessageToChannelAsBotRequestTextType): The type of the text, either message or card. It can't be
                both. Example: message.
        activity (Optional[SendMessageToChannelAsBotRequestActivity]):
        adaptive_card_content (Optional[str]): Pass the string by converting the generated JSON from
                https://adaptivecards.io/designer/. Directly paste json under "Text builder" or pass escaped JSON from
                "Expression editor" Example: {
                  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                  "type": "AdaptiveCard",
                  "version": "1.0",
                  "body": [
                    {
                      "type": "Container",
                      "items": [
                        {
                          "type": "TextBlock",
                          "text": "Publish Adaptive Card schema",
                          "weight": "bolder",
                          "size": "medium"
                        },
                        {
                          "type": "ColumnSet",
                          "columns": [
                            {
                              "type": "Column",
                              "width": "auto",
                              "items": [
                                {
                                  "type": "Image",
                                  "url":
                "https://pbs.twimg.com/profile_images/3647943215/d7f12830b3c17a5a9e4afcc370e3a37e_400x400.jpeg",
                                  "altText": "Matt Hidinger",
                                  "size": "small",
                                  "style": "person"
                                }
                              ]
                            },
                            {
                              "type": "Column",
                              "width": "stretch",
                              "items": [
                                {
                                  "type": "TextBlock",
                                  "text": "Matt Hidinger",
                                  "weight": "bolder",
                                  "wrap": true
                                },
                                {
                                  "type": "TextBlock",
                                  "spacing": "none",
                                  "text": "Created {{DATE(2017-02-14T06:08:39Z, SHORT)}}",
                                  "isSubtle": true,
                                  "wrap": true
                                }
                              ]
                            }
                          ]
                        }
                      ]
                    },
                    {
                      "type": "Container",
                      "items": [
                        {
                          "type": "TextBlock",
                          "text": "Now that we have defined the main rules and features of the format, we need to produce a
                schema and publish it to GitHub. The schema will be the starting point of our reference documentation.",
                          "wrap": true
                        },
                        {
                          "type": "FactSet",
                          "facts": [
                            {
                              "title": "Board:",
                              "value": "Adaptive Card"
                            },
                            {
                              "title": "List:",
                              "value": "Backlog"
                            },
                            {
                              "title": "Assigned to:",
                              "value": "Matt Hidinger"
                            },
                            {
                              "title": "Due date:",
                              "value": "Not set"
                            }
                          ]
                        }
                      ]
                    }
                  ],
                  "actions": [
                    {
                      "type": "Action.ShowCard",
                      "title": "Comment",
                      "card": {
                        "type": "AdaptiveCard",
                        "body": [
                          {
                            "type": "Input.Text",
                            "id": "comment",
                            "isMultiline": true,
                            "placeholder": "Enter your comment"
                          }
                        ],
                        "actions": [
                          {
                            "type": "Action.Submit",
                            "title": "OK"
                          }
                        ]
                      }
                    },
                    {
                      "type": "Action.OpenUrl",
                      "title": "View",
                      "url": "https://adaptivecards.io"
                    }
                  ]
                }
                .
        bot (Optional[SendMessageToChannelAsBotRequestBot]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    text_type: "SendMessageToChannelAsBotRequestTextType" = Field(alias="textType")
    channel_data: Optional["SendMessageToChannelAsBotRequestChannelData"] = Field(
        alias="channelData", default=None
    )
    activity: Optional["SendMessageToChannelAsBotRequestActivity"] = Field(
        alias="activity", default=None
    )
    adaptive_card_content: Optional[str] = Field(
        alias="adaptiveCardContent", default=None
    )
    bot: Optional["SendMessageToChannelAsBotRequestBot"] = Field(
        alias="bot", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SendMessageToChannelAsBotRequest"], src_dict: Dict[str, Any]
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

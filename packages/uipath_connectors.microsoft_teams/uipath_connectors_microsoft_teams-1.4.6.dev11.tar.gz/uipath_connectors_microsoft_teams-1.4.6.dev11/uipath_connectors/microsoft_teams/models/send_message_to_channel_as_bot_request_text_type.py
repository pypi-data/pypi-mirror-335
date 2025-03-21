from enum import Enum


class SendMessageToChannelAsBotRequestTextType(str, Enum):
    ADAPTIVE_CARD = "card"
    TEXT = "message"

    def __str__(self) -> str:
        return str(self.value)

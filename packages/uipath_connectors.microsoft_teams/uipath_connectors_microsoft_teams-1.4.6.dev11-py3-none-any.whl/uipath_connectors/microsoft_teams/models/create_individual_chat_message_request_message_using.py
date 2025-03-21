from enum import Enum


class CreateIndividualChatMessageRequestMessageUsing(str, Enum):
    CHAT_ID = "chatId"
    USER_EMAIL_UPN = "email"

    def __str__(self) -> str:
        return str(self.value)

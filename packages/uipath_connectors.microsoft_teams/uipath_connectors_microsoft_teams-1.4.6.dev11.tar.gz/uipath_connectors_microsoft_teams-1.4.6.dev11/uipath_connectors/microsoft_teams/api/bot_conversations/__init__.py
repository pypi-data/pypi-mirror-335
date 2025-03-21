from .send_message_to_channel_as_bot import sync as send_message_to_channel_as_bot
from .send_message_to_channel_as_bot import (
    asyncio as send_message_to_channel_as_bot_async,
)

__all__ = [
    "send_message_to_channel_as_bot",
    "send_message_to_channel_as_bot_async",
]

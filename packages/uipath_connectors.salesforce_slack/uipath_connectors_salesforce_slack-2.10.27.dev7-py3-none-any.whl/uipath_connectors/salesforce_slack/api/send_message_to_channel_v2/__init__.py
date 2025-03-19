from .send_message import sync as send_message
from .send_message import asyncio as send_message_async

__all__ = [
    "send_message",
    "send_message_async",
]

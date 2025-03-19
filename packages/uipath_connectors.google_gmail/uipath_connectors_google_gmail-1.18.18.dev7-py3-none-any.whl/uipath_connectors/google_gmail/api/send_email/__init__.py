from .send_email import sync as send_email
from .send_email import asyncio as send_email_async

__all__ = [
    "send_email",
    "send_email_async",
]

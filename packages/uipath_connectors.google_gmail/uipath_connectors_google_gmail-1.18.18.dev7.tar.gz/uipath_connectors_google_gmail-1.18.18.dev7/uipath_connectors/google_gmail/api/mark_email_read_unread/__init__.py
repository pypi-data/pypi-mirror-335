from .mark_email_read_unread import sync as mark_email_read_unread
from .mark_email_read_unread import asyncio as mark_email_read_unread_async

__all__ = [
    "mark_email_read_unread",
    "mark_email_read_unread_async",
]

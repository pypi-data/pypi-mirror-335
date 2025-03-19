from .forward_mail import sync as forward_mail
from .forward_mail import asyncio as forward_mail_async

__all__ = [
    "forward_mail",
    "forward_mail_async",
]

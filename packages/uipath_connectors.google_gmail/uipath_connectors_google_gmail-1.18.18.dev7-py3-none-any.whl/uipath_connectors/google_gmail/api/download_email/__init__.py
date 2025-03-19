from .download_email import sync as download_email
from .download_email import asyncio as download_email_async

__all__ = [
    "download_email",
    "download_email_async",
]

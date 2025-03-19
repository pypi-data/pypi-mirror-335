from .download_attachment import sync as download_attachment
from .download_attachment import asyncio as download_attachment_async

__all__ = [
    "download_attachment",
    "download_attachment_async",
]

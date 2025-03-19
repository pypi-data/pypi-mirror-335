from .upload_attachment import sync as upload_attachment
from .upload_attachment import asyncio as upload_attachment_async

__all__ = [
    "upload_attachment",
    "upload_attachment_async",
]

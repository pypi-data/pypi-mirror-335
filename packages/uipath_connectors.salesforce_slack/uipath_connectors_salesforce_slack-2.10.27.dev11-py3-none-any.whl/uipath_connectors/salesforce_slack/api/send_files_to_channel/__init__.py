from .upload_file import sync as upload_file
from .upload_file import asyncio as upload_file_async

__all__ = [
    "upload_file",
    "upload_file_async",
]

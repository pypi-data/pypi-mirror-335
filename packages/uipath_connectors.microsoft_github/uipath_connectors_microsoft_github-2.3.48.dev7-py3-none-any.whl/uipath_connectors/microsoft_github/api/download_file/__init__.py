from .download_file import sync as download_file
from .download_file import asyncio as download_file_async

__all__ = [
    "download_file",
    "download_file_async",
]

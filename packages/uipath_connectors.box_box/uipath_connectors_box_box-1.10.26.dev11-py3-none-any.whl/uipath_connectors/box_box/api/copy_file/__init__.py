from .copy_file import sync as copy_file
from .copy_file import asyncio as copy_file_async

__all__ = [
    "copy_file",
    "copy_file_async",
]

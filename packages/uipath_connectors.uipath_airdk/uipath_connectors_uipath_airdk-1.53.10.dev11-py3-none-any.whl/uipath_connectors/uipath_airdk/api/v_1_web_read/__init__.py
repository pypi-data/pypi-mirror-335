from .web_reader import sync as web_reader
from .web_reader import asyncio as web_reader_async

__all__ = [
    "web_reader",
    "web_reader_async",
]

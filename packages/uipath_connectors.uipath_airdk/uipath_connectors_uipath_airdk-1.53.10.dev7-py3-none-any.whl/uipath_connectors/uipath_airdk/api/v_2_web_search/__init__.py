from .web_search import sync as web_search
from .web_search import asyncio as web_search_async

__all__ = [
    "web_search",
    "web_search_async",
]

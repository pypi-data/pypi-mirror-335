from .translate import sync as translate
from .translate import asyncio as translate_async

__all__ = [
    "translate",
    "translate_async",
]

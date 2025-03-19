from .named_entity_recognition import sync as named_entity_recognition
from .named_entity_recognition import asyncio as named_entity_recognition_async

__all__ = [
    "named_entity_recognition",
    "named_entity_recognition_async",
]

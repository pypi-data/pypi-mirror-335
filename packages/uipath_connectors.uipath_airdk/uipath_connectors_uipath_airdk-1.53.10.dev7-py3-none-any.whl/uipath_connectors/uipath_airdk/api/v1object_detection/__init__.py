from .object_detection import sync as object_detection
from .object_detection import asyncio as object_detection_async

__all__ = [
    "object_detection",
    "object_detection_async",
]

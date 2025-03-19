from .language_detection import sync as language_detection
from .language_detection import asyncio as language_detection_async

__all__ = [
    "language_detection",
    "language_detection_async",
]

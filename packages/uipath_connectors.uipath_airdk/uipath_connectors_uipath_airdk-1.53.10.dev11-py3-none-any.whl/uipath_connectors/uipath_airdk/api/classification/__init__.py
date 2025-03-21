from .image_classification import sync as image_classification
from .image_classification import asyncio as image_classification_async

__all__ = [
    "image_classification",
    "image_classification_async",
]

from .semantic_similarity import sync as semantic_similarity
from .semantic_similarity import asyncio as semantic_similarity_async

__all__ = [
    "semantic_similarity",
    "semantic_similarity_async",
]

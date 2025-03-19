from .signature_similarity import sync as signature_similarity
from .signature_similarity import asyncio as signature_similarity_async

__all__ = [
    "signature_similarity",
    "signature_similarity_async",
]

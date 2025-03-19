from .sentiment_analysis import sync as sentiment_analysis
from .sentiment_analysis import asyncio as sentiment_analysis_async

__all__ = [
    "sentiment_analysis",
    "sentiment_analysis_async",
]

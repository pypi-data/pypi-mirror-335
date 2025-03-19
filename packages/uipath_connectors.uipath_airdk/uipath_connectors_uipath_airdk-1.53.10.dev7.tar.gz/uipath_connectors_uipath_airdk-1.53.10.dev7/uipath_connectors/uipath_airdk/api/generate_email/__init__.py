from .generate_email import sync as generate_email
from .generate_email import asyncio as generate_email_async

__all__ = [
    "generate_email",
    "generate_email_async",
]

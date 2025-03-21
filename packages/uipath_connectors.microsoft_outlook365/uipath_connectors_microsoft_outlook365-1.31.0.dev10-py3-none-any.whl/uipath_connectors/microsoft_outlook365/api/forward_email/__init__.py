from .forward_email import sync as forward_email
from .forward_email import asyncio as forward_email_async

__all__ = [
    "forward_email",
    "forward_email_async",
]

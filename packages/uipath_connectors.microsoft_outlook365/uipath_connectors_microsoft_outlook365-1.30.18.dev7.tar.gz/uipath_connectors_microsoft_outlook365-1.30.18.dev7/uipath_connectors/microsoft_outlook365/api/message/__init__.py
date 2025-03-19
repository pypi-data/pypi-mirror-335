from .delete_email import sync as delete_email
from .delete_email import asyncio as delete_email_async
from .list_email import sync as list_email
from .list_email import asyncio as list_email_async

__all__ = [
    "delete_email",
    "delete_email_async",
    "list_email",
    "list_email_async",
]

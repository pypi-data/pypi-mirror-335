from .get_comments import sync as get_comments
from .get_comments import asyncio as get_comments_async

__all__ = [
    "get_comments",
    "get_comments_async",
]

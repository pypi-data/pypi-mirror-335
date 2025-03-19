from .upsert_issue import sync as upsert_issue
from .upsert_issue import asyncio as upsert_issue_async

__all__ = [
    "upsert_issue",
    "upsert_issue_async",
]

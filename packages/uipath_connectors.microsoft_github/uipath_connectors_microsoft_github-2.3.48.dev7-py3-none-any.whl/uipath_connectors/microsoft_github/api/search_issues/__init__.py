from .search_issues import sync as search_issues
from .search_issues import asyncio as search_issues_async

__all__ = [
    "search_issues",
    "search_issues_async",
]

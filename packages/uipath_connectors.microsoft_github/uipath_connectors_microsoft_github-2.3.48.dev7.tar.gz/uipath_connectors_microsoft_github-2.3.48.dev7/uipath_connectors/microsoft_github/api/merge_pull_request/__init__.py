from .merge_pull import sync as merge_pull
from .merge_pull import asyncio as merge_pull_async

__all__ = [
    "merge_pull",
    "merge_pull_async",
]

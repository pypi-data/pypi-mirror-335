from .write_column import sync as write_column
from .write_column import asyncio as write_column_async

__all__ = [
    "write_column",
    "write_column_async",
]

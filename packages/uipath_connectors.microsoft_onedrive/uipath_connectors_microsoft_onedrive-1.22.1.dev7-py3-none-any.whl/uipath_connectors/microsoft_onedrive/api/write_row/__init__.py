from .write_row import sync as write_row
from .write_row import asyncio as write_row_async

__all__ = [
    "write_row",
    "write_row_async",
]

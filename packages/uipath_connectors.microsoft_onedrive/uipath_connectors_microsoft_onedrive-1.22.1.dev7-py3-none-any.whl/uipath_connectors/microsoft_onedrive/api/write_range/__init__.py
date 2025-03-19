from .write_range import sync as write_range
from .write_range import asyncio as write_range_async

__all__ = [
    "write_range",
    "write_range_async",
]

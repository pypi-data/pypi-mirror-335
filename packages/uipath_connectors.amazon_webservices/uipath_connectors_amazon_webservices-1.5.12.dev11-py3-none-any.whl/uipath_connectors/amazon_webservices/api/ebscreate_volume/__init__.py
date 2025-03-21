from .create_volume import sync as create_volume
from .create_volume import asyncio as create_volume_async

__all__ = [
    "create_volume",
    "create_volume_async",
]

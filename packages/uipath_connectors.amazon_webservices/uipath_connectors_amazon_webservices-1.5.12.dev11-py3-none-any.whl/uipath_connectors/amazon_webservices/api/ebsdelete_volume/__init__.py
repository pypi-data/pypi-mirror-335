from .delete_volume import sync as delete_volume
from .delete_volume import asyncio as delete_volume_async

__all__ = [
    "delete_volume",
    "delete_volume_async",
]

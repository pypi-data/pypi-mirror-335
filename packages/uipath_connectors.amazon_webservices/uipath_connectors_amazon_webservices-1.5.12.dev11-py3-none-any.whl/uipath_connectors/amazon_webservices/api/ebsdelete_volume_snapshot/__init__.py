from .delete_snapshot import sync as delete_snapshot
from .delete_snapshot import asyncio as delete_snapshot_async

__all__ = [
    "delete_snapshot",
    "delete_snapshot_async",
]

from .create_volume_snapshot import sync as create_volume_snapshot
from .create_volume_snapshot import asyncio as create_volume_snapshot_async

__all__ = [
    "create_volume_snapshot",
    "create_volume_snapshot_async",
]

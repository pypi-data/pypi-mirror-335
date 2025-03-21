from .detach_volume_from_instance import sync as detach_volume_from_instance
from .detach_volume_from_instance import asyncio as detach_volume_from_instance_async

__all__ = [
    "detach_volume_from_instance",
    "detach_volume_from_instance_async",
]

from .attach_volume_to_instance import sync as attach_volume_to_instance
from .attach_volume_to_instance import asyncio as attach_volume_to_instance_async

__all__ = [
    "attach_volume_to_instance",
    "attach_volume_to_instance_async",
]

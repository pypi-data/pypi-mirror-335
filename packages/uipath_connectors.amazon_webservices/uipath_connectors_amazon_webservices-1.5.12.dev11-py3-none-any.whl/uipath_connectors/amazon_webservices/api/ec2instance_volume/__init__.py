from .get_instance_volumes import sync as get_instance_volumes
from .get_instance_volumes import asyncio as get_instance_volumes_async

__all__ = [
    "get_instance_volumes",
    "get_instance_volumes_async",
]

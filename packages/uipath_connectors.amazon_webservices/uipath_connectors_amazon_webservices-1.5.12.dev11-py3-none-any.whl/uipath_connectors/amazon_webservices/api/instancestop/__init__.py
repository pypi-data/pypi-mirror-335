from .stop_instance import sync as stop_instance
from .stop_instance import asyncio as stop_instance_async

__all__ = [
    "stop_instance",
    "stop_instance_async",
]

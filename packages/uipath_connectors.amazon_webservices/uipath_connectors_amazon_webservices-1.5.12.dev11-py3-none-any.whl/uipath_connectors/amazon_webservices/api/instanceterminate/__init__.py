from .terminate_instance import sync as terminate_instance
from .terminate_instance import asyncio as terminate_instance_async

__all__ = [
    "terminate_instance",
    "terminate_instance_async",
]

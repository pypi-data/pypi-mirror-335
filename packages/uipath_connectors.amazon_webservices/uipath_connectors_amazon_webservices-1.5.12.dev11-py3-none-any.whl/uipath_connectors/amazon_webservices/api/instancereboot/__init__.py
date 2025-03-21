from .reboot_instance import sync as reboot_instance
from .reboot_instance import asyncio as reboot_instance_async

__all__ = [
    "reboot_instance",
    "reboot_instance_async",
]

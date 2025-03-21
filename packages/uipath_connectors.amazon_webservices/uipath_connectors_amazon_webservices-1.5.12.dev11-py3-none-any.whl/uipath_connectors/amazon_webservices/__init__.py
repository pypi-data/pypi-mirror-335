from typing import Any
from .api import AmazonWebservices  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the amazon_webservices connector."""
    connections.amazon_webservices = lambda instance_id: AmazonWebservices(
        instance_id=instance_id, client=connections.client
    )

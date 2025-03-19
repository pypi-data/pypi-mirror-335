from typing import Any
from .api import BoxBox  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the box_box connector."""
    connections.box_box = lambda instance_id: BoxBox(
        instance_id=instance_id, client=connections.client
    )

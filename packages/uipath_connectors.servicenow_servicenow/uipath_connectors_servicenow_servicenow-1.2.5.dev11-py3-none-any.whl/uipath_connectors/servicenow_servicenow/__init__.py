from typing import Any
from .api import ServicenowServicenow  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the servicenow_servicenow connector."""
    connections.servicenow_servicenow = lambda instance_id: ServicenowServicenow(
        instance_id=instance_id, client=connections.client
    )

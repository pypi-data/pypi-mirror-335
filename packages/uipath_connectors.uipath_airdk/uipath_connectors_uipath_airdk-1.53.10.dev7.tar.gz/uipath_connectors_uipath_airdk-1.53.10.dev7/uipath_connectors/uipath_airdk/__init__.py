from typing import Any
from .api import UiPathAirdk  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the uipath_airdk connector."""
    connections.uipath_airdk = lambda instance_id: UiPathAirdk(
        instance_id=instance_id, client=connections.client
    )

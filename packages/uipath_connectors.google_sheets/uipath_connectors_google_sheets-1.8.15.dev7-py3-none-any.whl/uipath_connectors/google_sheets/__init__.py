from typing import Any
from .api import GoogleSheets  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the google_sheets connector."""
    connections.google_sheets = lambda instance_id: GoogleSheets(
        instance_id=instance_id, client=connections.client
    )

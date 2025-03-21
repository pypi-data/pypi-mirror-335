from typing import Any
from .api import GoogleDrive  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the google_drive connector."""
    connections.google_drive = lambda instance_id: GoogleDrive(
        instance_id=instance_id, client=connections.client
    )

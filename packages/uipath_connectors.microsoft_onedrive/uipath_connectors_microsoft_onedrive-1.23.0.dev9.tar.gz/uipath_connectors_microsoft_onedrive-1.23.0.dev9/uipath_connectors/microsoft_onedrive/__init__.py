from typing import Any
from .api import MicrosoftOnedrive  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the microsoft_onedrive connector."""
    connections.microsoft_onedrive = lambda instance_id: MicrosoftOnedrive(
        instance_id=instance_id, client=connections.client
    )

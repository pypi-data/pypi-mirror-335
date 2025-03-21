from typing import Any
from .api import GoogleGmail  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the google_gmail connector."""
    connections.google_gmail = lambda instance_id: GoogleGmail(
        instance_id=instance_id, client=connections.client
    )

from typing import Any
from .api import MicrosoftOutlook365  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the microsoft_outlook365 connector."""
    connections.microsoft_outlook365 = lambda instance_id: MicrosoftOutlook365(
        instance_id=instance_id, client=connections.client
    )

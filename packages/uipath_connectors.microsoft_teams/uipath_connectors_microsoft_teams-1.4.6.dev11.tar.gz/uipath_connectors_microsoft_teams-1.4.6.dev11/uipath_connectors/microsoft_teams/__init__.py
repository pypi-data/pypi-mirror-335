from typing import Any
from .api import MicrosoftTeams  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the microsoft_teams connector."""
    connections.microsoft_teams = lambda instance_id: MicrosoftTeams(
        instance_id=instance_id, client=connections.client
    )

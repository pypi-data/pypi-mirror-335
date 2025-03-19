from typing import Any
from .api import MicrosoftGithub  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the microsoft_github connector."""
    connections.microsoft_github = lambda instance_id: MicrosoftGithub(
        instance_id=instance_id, client=connections.client
    )

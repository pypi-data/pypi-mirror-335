from typing import Any
from .api import AtlassianJira  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the atlassian_jira connector."""
    connections.atlassian_jira = lambda instance_id: AtlassianJira(
        instance_id=instance_id, client=connections.client
    )

from typing import Any
from .api import SalesforceSlack  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the salesforce_slack connector."""
    connections.salesforce_slack = lambda instance_id: SalesforceSlack(
        instance_id=instance_id, client=connections.client
    )

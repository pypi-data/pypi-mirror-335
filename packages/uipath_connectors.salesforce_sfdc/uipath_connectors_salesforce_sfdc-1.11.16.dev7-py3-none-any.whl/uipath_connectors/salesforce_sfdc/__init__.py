from typing import Any
from .api import SalesforceSfdc  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the salesforce_sfdc connector."""
    connections.salesforce_sfdc = lambda instance_id: SalesforceSfdc(
        instance_id=instance_id, client=connections.client
    )

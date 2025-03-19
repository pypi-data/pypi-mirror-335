from typing import Any
from .api import OracleNetsuite  # type: ignore
from .models import *  # type: ignore


def register_connector(connections: Any):
    """Register the oracle_netsuite connector."""
    connections.oracle_netsuite = lambda instance_id: OracleNetsuite(
        instance_id=instance_id, client=connections.client
    )

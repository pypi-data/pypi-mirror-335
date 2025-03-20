"""
Main interface for ce service.

[Documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_ce/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_ce import (
        Client,
        CostExplorerClient,
    )

    session = Session()
    client: CostExplorerClient = session.client("ce")
    ```
"""

from .client import CostExplorerClient

Client = CostExplorerClient

__all__ = ("Client", "CostExplorerClient")

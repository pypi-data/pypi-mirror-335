"""
Main interface for schemas service.

[Documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_schemas/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_schemas import (
        Client,
        CodeBindingExistsWaiter,
        ListDiscoverersPaginator,
        ListRegistriesPaginator,
        ListSchemaVersionsPaginator,
        ListSchemasPaginator,
        SchemasClient,
        SearchSchemasPaginator,
    )

    session = Session()
    client: SchemasClient = session.client("schemas")

    code_binding_exists_waiter: CodeBindingExistsWaiter = client.get_waiter("code_binding_exists")

    list_discoverers_paginator: ListDiscoverersPaginator = client.get_paginator("list_discoverers")
    list_registries_paginator: ListRegistriesPaginator = client.get_paginator("list_registries")
    list_schema_versions_paginator: ListSchemaVersionsPaginator = client.get_paginator("list_schema_versions")
    list_schemas_paginator: ListSchemasPaginator = client.get_paginator("list_schemas")
    search_schemas_paginator: SearchSchemasPaginator = client.get_paginator("search_schemas")
    ```
"""

from .client import SchemasClient
from .paginator import (
    ListDiscoverersPaginator,
    ListRegistriesPaginator,
    ListSchemasPaginator,
    ListSchemaVersionsPaginator,
    SearchSchemasPaginator,
)
from .waiter import CodeBindingExistsWaiter

Client = SchemasClient


__all__ = (
    "Client",
    "CodeBindingExistsWaiter",
    "ListDiscoverersPaginator",
    "ListRegistriesPaginator",
    "ListSchemaVersionsPaginator",
    "ListSchemasPaginator",
    "SchemasClient",
    "SearchSchemasPaginator",
)

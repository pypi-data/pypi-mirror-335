"""
Main interface for imagebuilder service.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_imagebuilder/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from boto3.session import Session
    from types_boto3_imagebuilder import (
        Client,
        ImagebuilderClient,
    )

    session = Session()
    client: ImagebuilderClient = session.client("imagebuilder")
    ```
"""

from .client import ImagebuilderClient

Client = ImagebuilderClient


__all__ = ("Client", "ImagebuilderClient")

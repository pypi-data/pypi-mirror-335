"""
Main interface for chime-sdk-identity service.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_chime_sdk_identity/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from boto3.session import Session
    from types_boto3_chime_sdk_identity import (
        ChimeSDKIdentityClient,
        Client,
    )

    session = Session()
    client: ChimeSDKIdentityClient = session.client("chime-sdk-identity")
    ```
"""

from .client import ChimeSDKIdentityClient

Client = ChimeSDKIdentityClient


__all__ = ("ChimeSDKIdentityClient", "Client")

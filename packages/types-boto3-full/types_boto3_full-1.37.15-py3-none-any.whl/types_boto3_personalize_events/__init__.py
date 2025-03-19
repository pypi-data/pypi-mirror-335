"""
Main interface for personalize-events service.

[Documentation](https://youtype.github.io/types_boto3_docs/types_boto3_personalize_events/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from boto3.session import Session
    from types_boto3_personalize_events import (
        Client,
        PersonalizeEventsClient,
    )

    session = Session()
    client: PersonalizeEventsClient = session.client("personalize-events")
    ```
"""

from .client import PersonalizeEventsClient

Client = PersonalizeEventsClient


__all__ = ("Client", "PersonalizeEventsClient")

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SessionGetEventsParams"]


class SessionGetEventsParams(TypedDict, total=False):
    all: bool
    """Get all events"""

    last_event_id: Annotated[int, PropertyInfo(alias="lastEventId")]
    """last known event id"""

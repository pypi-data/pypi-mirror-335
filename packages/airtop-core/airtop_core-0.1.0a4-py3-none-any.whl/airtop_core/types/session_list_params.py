# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SessionListParams"]


class SessionListParams(TypedDict, total=False):
    limit: int
    """Limit for pagination."""

    offset: int
    """Offset for pagination."""

    session_ids: Annotated[Optional[List[str]], PropertyInfo(alias="sessionIds")]
    """A comma-separated list of IDs of the sessions to retrieve."""

    status: Literal["awaitingCapacity", "initializing", "running", "ended", "completed", "cancelled", "all"]
    """Status of the session to get."""

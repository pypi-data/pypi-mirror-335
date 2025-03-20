# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .airtop_pagination import AirtopPagination
from .external_session_with_connection_info import ExternalSessionWithConnectionInfo

__all__ = ["SessionsWithPagination"]


class SessionsWithPagination(BaseModel):
    pagination: AirtopPagination
    """Pagination details."""

    sessions: Optional[List[ExternalSessionWithConnectionInfo]] = None
    """List of sessions."""

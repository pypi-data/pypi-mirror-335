# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from ..._models import BaseModel

__all__ = ["Issue"]


class Issue(BaseModel):
    message: str
    """Message describing the issue."""

    code: Optional[str] = None
    """Issue code."""

    details: Optional[Dict[str, object]] = None
    """Any associated details."""

    reason: Optional[str] = None
    """Underlying reason for the issue."""

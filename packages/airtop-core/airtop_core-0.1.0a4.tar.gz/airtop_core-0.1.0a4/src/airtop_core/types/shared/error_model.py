# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .error_detail import ErrorDetail

__all__ = ["ErrorModel"]


class ErrorModel(BaseModel):
    detail: Optional[str] = None
    """A human-readable explanation specific to this occurrence of the problem."""

    errors: Optional[List[ErrorDetail]] = None
    """Optional list of individual error details"""

    instance: Optional[str] = None
    """A URI reference that identifies the specific occurrence of the problem."""

    status: Optional[int] = None
    """HTTP status code"""

    title: Optional[str] = None
    """A short, human-readable summary of the problem type.

    This value should not change between occurrences of the error.
    """

    type: Optional[str] = None
    """A URI reference to human-readable documentation for the error."""

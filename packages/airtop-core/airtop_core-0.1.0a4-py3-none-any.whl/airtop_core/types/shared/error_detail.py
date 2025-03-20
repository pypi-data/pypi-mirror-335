# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ErrorDetail"]


class ErrorDetail(BaseModel):
    location: Optional[str] = None
    """Where the error occurred, e.g. 'body.items[3].tags' or 'path.thing-id'"""

    message: Optional[str] = None
    """Error message text"""

    value: Optional[object] = None
    """The value at the given location"""

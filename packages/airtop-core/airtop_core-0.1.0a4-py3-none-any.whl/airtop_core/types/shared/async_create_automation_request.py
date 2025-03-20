# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .async_config import AsyncConfig

__all__ = ["AsyncCreateAutomationRequest"]


class AsyncCreateAutomationRequest(BaseModel):
    async_: Optional[AsyncConfig] = FieldInfo(alias="async", default=None)
    """Async configuration options."""

    client_request_id: Optional[str] = FieldInfo(alias="clientRequestId", default=None)

    configuration: Optional[object] = None
    """Request configuration"""

    cost_threshold_credits: Optional[int] = FieldInfo(alias="costThresholdCredits", default=None)
    """A credit threshold that, once exceeded, will cause the operation to be
    cancelled.

    Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).
    """

    time_threshold_seconds: Optional[int] = FieldInfo(alias="timeThresholdSeconds", default=None)
    """
    A time threshold in seconds that, once exceeded, will cause the operation to be
    cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).

    This setting does not extend the maximum session duration provided at the time
    of session creation.
    """

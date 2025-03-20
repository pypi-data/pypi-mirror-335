# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .error_body import ErrorBody

__all__ = ["SessionEventMessage"]


class SessionEventMessage(BaseModel):
    id: str
    """ID of the session"""

    event: str
    """Event name"""

    event_time: datetime = FieldInfo(alias="eventTime")
    """Date and Time of the event"""

    error: Optional[ErrorBody] = None
    """Error message"""

    event_data: Optional[object] = FieldInfo(alias="eventData", default=None)
    """Data of the event"""

    event_id: Optional[int] = FieldInfo(alias="eventId", default=None)
    """Event ID"""

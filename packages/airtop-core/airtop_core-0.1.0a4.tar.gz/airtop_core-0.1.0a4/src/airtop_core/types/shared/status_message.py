# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["StatusMessage"]


class StatusMessage(BaseModel):
    id: str
    """ID of the session"""

    event: str
    """Event name"""

    event_time: datetime = FieldInfo(alias="eventTime")
    """Date and Time of the event"""

    status: Literal["awaitingCapacity", "initializing", "running", "ended", "error", "disconnected"]
    """Status of the session"""

    event_id: Optional[int] = FieldInfo(alias="eventId", default=None)
    """Event ID"""

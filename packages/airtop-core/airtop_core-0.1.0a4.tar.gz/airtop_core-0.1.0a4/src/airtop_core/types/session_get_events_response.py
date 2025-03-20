# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .shared.error_message import ErrorMessage
from .shared.status_message import StatusMessage
from .shared.window_event_message import WindowEventMessage
from .shared.session_event_message import SessionEventMessage

__all__ = ["SessionGetEventsResponse", "EventStatus", "EventError", "EventWindowEvent", "EventSessionEvent"]


class EventStatus(BaseModel):
    data: StatusMessage

    event: Literal["status"]
    """The event name."""

    id: Optional[int] = None
    """The event ID."""

    retry: Optional[int] = None
    """The retry time in milliseconds."""


class EventError(BaseModel):
    data: ErrorMessage

    event: Literal["error"]
    """The event name."""

    id: Optional[int] = None
    """The event ID."""

    retry: Optional[int] = None
    """The retry time in milliseconds."""


class EventWindowEvent(BaseModel):
    data: WindowEventMessage

    event: Literal["windowEvent"]
    """The event name."""

    id: Optional[int] = None
    """The event ID."""

    retry: Optional[int] = None
    """The retry time in milliseconds."""


class EventSessionEvent(BaseModel):
    data: SessionEventMessage

    event: Literal["sessionEvent"]
    """The event name."""

    id: Optional[int] = None
    """The event ID."""

    retry: Optional[int] = None
    """The retry time in milliseconds."""


SessionGetEventsResponse: TypeAlias = Union[EventStatus, EventError, EventWindowEvent, EventSessionEvent]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.paginated_extraction_config import PaginatedExtractionConfig

__all__ = ["WindowPaginatedExtractionParams"]


class WindowPaginatedExtractionParams(TypedDict, total=False):
    session_id: Required[Annotated[str, PropertyInfo(alias="sessionId")]]
    """The session id for the window."""

    prompt: Required[str]
    """
    A prompt providing the Airtop AI model with additional direction or constraints
    about the page and the details you want to extract from the page.
    """

    client_request_id: Annotated[str, PropertyInfo(alias="clientRequestId")]

    configuration: PaginatedExtractionConfig
    """Request configuration"""

    cost_threshold_credits: Annotated[int, PropertyInfo(alias="costThresholdCredits")]
    """A credit threshold that, once exceeded, will cause the operation to be
    cancelled.

    Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).
    """

    time_threshold_seconds: Annotated[int, PropertyInfo(alias="timeThresholdSeconds")]
    """
    A time threshold in seconds that, once exceeded, will cause the operation to be
    cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).

    This setting does not extend the maximum session duration provided at the time
    of session creation.
    """

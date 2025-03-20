# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.scroll_by_config import ScrollByConfig
from .shared_params.scroll_to_edge_config import ScrollToEdgeConfig
from .shared_params.micro_interaction_config import MicroInteractionConfig

__all__ = ["WindowScrollParams"]


class WindowScrollParams(TypedDict, total=False):
    session_id: Required[Annotated[str, PropertyInfo(alias="sessionId")]]
    """The session id for the window."""

    client_request_id: Annotated[str, PropertyInfo(alias="clientRequestId")]

    configuration: MicroInteractionConfig
    """Request configuration"""

    cost_threshold_credits: Annotated[int, PropertyInfo(alias="costThresholdCredits")]
    """A credit threshold that, once exceeded, will cause the operation to be
    cancelled.

    Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).
    """

    scroll_by: Annotated[ScrollByConfig, PropertyInfo(alias="scrollBy")]
    """
    The amount of pixels/percentage to scroll horizontally or vertically relative to
    the current scroll position. Positive values scroll right and down, negative
    values scroll left and up. If a scrollToElement value is provided,
    scrollBy/scrollToEdge values will be ignored.
    """

    scroll_to_edge: Annotated[ScrollToEdgeConfig, PropertyInfo(alias="scrollToEdge")]
    """Scroll to the top or bottom of the page, or to the left or right of the page.

    ScrollToEdge values will take precedence over the scrollBy values, and
    scrollToEdge will be executed first. If a scrollToElement value is provided,
    scrollToEdge/scrollBy values will be ignored.
    """

    scroll_to_element: Annotated[str, PropertyInfo(alias="scrollToElement")]
    """A natural language description of where to scroll (e.g.

    'the search box', 'username field'). The interaction will be aborted if the
    target element cannot be found. If provided, scrollToEdge/scrollBy values will
    be ignored.
    """

    scroll_within: Annotated[str, PropertyInfo(alias="scrollWithin")]
    """A natural language description of the scrollable area on the web page.

    This identifies the container or region that should be scrolled. If missing, the
    entire page will be scrolled. You can also describe a visible reference point
    inside the container. Note: This is different from scrollToElement, which
    specifies the target element to scroll to. The target may be located inside the
    scrollable area defined by scrollWithin.
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

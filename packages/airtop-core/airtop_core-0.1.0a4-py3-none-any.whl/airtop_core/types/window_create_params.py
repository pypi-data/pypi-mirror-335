# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WindowCreateParams"]


class WindowCreateParams(TypedDict, total=False):
    screen_resolution: Annotated[str, PropertyInfo(alias="screenResolution")]
    """Affects the live view configuration.

    By default, a live view will fill the parent frame (or local window if loaded
    directly) when initially loaded, causing the browser window to be resized to
    match. This parameter can be used to instead configure the returned liveViewUrl
    so that the live view is loaded with fixed dimensions (e.g. 1280x720), resizing
    the browser window to match, and then disallows any further resizing from the
    live view.
    """

    url: str
    """Initial url to navigate to"""

    wait_until: Annotated[Literal["load", "domContentLoaded", "complete", "noWait"], PropertyInfo(alias="waitUntil")]
    """Wait until the specified loading event occurs.

    Defaults to 'load', which waits until the page dom and it's assets have loaded.
    'domContentLoaded' will wait until the dom has loaded, 'complete' will wait
    until the page and all it's iframes have loaded it's dom and assets. 'noWait'
    will not wait for any loading event and will return immediately.
    """

    wait_until_timeout_seconds: Annotated[int, PropertyInfo(alias="waitUntilTimeoutSeconds")]
    """
    Maximum time in seconds to wait for the specified loading event to occur before
    timing out.
    """

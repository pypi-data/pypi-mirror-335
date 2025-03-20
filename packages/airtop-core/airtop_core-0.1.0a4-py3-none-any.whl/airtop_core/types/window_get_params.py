# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WindowGetParams"]


class WindowGetParams(TypedDict, total=False):
    session_id: Required[Annotated[str, PropertyInfo(alias="sessionId")]]
    """ID of the session that owns the window."""

    disable_resize: Annotated[bool, PropertyInfo(alias="disableResize")]
    """Affects the live view configuration.

    Set to true to configure the returned liveViewUrl so that the ability to resize
    the browser window from the live view is disabled (resizing is allowed by
    default). Note that, at initial load, the live view will automatically fill the
    parent frame (or local window if loaded directly) and cause the browser window
    to be resized to match. This parameter does not affect that initial load
    behavior. See screenResolution for a way to set a fixed size for the live view.
    """

    include_navigation_bar: Annotated[bool, PropertyInfo(alias="includeNavigationBar")]
    """Affects the live view configuration.

    A navigation bar is not shown in the live view of a browser by default. Set this
    to true to configure the returned liveViewUrl so that a navigation bar is
    rendered, allowing users to easily navigate the browser to other pages from the
    live view.
    """

    screen_resolution: Annotated[str, PropertyInfo(alias="screenResolution")]
    """Affects the live view configuration.

    By default, a live view will fill the parent frame (or local window if loaded
    directly) when initially loaded, causing the browser window to be resized to
    match. This parameter can be used to instead configure the returned liveViewUrl
    so that the live view is loaded with fixed dimensions (e.g. 1280x720), resizing
    the browser window to match, and then disallows any further resizing from the
    live view.
    """

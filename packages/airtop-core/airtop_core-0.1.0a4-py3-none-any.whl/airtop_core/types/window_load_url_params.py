# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["WindowLoadURLParams"]


class WindowLoadURLParams(TypedDict, total=False):
    session_id: Required[Annotated[str, PropertyInfo(alias="sessionId")]]
    """ID of the session that owns the window."""

    url: Required[str]
    """Url to navigate to"""

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

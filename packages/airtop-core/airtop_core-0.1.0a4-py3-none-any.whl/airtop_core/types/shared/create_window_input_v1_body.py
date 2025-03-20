# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CreateWindowInputV1Body"]


class CreateWindowInputV1Body(BaseModel):
    screen_resolution: Optional[str] = FieldInfo(alias="screenResolution", default=None)
    """Affects the live view configuration.

    By default, a live view will fill the parent frame (or local window if loaded
    directly) when initially loaded, causing the browser window to be resized to
    match. This parameter can be used to instead configure the returned liveViewUrl
    so that the live view is loaded with fixed dimensions (e.g. 1280x720), resizing
    the browser window to match, and then disallows any further resizing from the
    live view.
    """

    url: Optional[str] = None
    """Initial url to navigate to"""

    wait_until: Optional[Literal["load", "domContentLoaded", "complete", "noWait"]] = FieldInfo(
        alias="waitUntil", default=None
    )
    """Wait until the specified loading event occurs.

    Defaults to 'load', which waits until the page dom and it's assets have loaded.
    'domContentLoaded' will wait until the dom has loaded, 'complete' will wait
    until the page and all it's iframes have loaded it's dom and assets. 'noWait'
    will not wait for any loading event and will return immediately.
    """

    wait_until_timeout_seconds: Optional[int] = FieldInfo(alias="waitUntilTimeoutSeconds", default=None)
    """
    Maximum time in seconds to wait for the specified loading event to occur before
    timing out.
    """

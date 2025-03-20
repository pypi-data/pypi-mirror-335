# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["WindowLoadURLV1Body"]


class WindowLoadURLV1Body(BaseModel):
    url: str
    """Url to navigate to"""

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

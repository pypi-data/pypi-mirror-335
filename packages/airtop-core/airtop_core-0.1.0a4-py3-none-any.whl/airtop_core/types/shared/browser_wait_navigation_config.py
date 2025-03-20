# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["BrowserWaitNavigationConfig"]


class BrowserWaitNavigationConfig(BaseModel):
    timeout_seconds: Optional[int] = FieldInfo(alias="timeoutSeconds", default=None)
    """The maximum time to wait for the navigation to complete, in seconds.

    Defaults to 30 (30 seconds).
    """

    wait_until: Optional[Literal["load", "domcontentloaded", "networkidle0", "networkidle2"]] = FieldInfo(
        alias="waitUntil", default=None
    )
    """The condition to wait for the navigation to complete. Defaults to 'load'."""

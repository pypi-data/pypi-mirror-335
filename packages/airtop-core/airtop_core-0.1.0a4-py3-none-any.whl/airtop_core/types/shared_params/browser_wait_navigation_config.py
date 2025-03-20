# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["BrowserWaitNavigationConfig"]


class BrowserWaitNavigationConfig(TypedDict, total=False):
    timeout_seconds: Annotated[int, PropertyInfo(alias="timeoutSeconds")]
    """The maximum time to wait for the navigation to complete, in seconds.

    Defaults to 30 (30 seconds).
    """

    wait_until: Annotated[
        Literal["load", "domcontentloaded", "networkidle0", "networkidle2"], PropertyInfo(alias="waitUntil")
    ]
    """The condition to wait for the navigation to complete. Defaults to 'load'."""

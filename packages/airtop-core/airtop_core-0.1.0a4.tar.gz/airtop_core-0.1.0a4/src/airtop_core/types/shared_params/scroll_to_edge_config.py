# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ScrollToEdgeConfig"]


class ScrollToEdgeConfig(TypedDict, total=False):
    x_axis: Annotated[str, PropertyInfo(alias="xAxis")]
    """Scroll to the left or right of the page."""

    y_axis: Annotated[str, PropertyInfo(alias="yAxis")]
    """Scroll to the top or bottom of the page."""

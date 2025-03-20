# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ScrollByConfig"]


class ScrollByConfig(TypedDict, total=False):
    x_axis: Annotated[str, PropertyInfo(alias="xAxis")]
    """The amount of pixels/percentage to scroll horizontally.

    Percentage values should be between 0 and 100. Positive values scroll right,
    negative values scroll left.
    """

    y_axis: Annotated[str, PropertyInfo(alias="yAxis")]
    """The amount of pixels/percentage to scroll vertically.

    Percentage values should be between 0 and 100. Positive values scroll down,
    negative values scroll up.
    """

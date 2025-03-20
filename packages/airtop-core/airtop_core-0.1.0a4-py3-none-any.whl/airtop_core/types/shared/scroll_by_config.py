# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ScrollByConfig"]


class ScrollByConfig(BaseModel):
    x_axis: Optional[str] = FieldInfo(alias="xAxis", default=None)
    """The amount of pixels/percentage to scroll horizontally.

    Percentage values should be between 0 and 100. Positive values scroll right,
    negative values scroll left.
    """

    y_axis: Optional[str] = FieldInfo(alias="yAxis", default=None)
    """The amount of pixels/percentage to scroll vertically.

    Percentage values should be between 0 and 100. Positive values scroll down,
    negative values scroll up.
    """

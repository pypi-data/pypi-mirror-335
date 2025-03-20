# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ScrollToEdgeConfig"]


class ScrollToEdgeConfig(BaseModel):
    x_axis: Optional[str] = FieldInfo(alias="xAxis", default=None)
    """Scroll to the left or right of the page."""

    y_axis: Optional[str] = FieldInfo(alias="yAxis", default=None)
    """Scroll to the top or bottom of the page."""

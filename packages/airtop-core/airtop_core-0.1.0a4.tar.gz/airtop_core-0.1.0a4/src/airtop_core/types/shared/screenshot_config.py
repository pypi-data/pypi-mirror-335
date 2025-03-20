# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ScreenshotConfig"]


class ScreenshotConfig(BaseModel):
    max_height: Optional[int] = FieldInfo(alias="maxHeight", default=None)
    """Maximum height of the screenshot in pixels.

    The screenshot will be scaled down to fit within this height if necessary,
    preserving the aspect ratio.
    """

    max_width: Optional[int] = FieldInfo(alias="maxWidth", default=None)
    """Maximum width of the screenshot in pixels.

    The screenshot will be scaled down to fit within this width if necessary,
    preserving the aspect ratio.
    """

    quality: Optional[int] = None
    """JPEG quality (1-100).

    Note that this option is still in development and may not work as expected.
    """

    scope: Optional[Literal["viewport"]] = None
    """Whether to capture the current viewport or whole page.

    Only viewport is currently supported.
    """

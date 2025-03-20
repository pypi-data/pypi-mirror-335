# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["ScreenshotConfig"]


class ScreenshotConfig(TypedDict, total=False):
    max_height: Annotated[int, PropertyInfo(alias="maxHeight")]
    """Maximum height of the screenshot in pixels.

    The screenshot will be scaled down to fit within this height if necessary,
    preserving the aspect ratio.
    """

    max_width: Annotated[int, PropertyInfo(alias="maxWidth")]
    """Maximum width of the screenshot in pixels.

    The screenshot will be scaled down to fit within this width if necessary,
    preserving the aspect ratio.
    """

    quality: int
    """JPEG quality (1-100).

    Note that this option is still in development and may not work as expected.
    """

    scope: Literal["viewport"]
    """Whether to capture the current viewport or whole page.

    Only viewport is currently supported.
    """

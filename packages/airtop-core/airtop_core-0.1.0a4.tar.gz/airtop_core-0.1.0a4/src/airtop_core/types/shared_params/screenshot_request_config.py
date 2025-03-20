# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from .screenshot_config import ScreenshotConfig

__all__ = ["ScreenshotRequestConfig"]


class ScreenshotRequestConfig(TypedDict, total=False):
    screenshot: ScreenshotConfig
    """Optional configuration for the screenshot."""

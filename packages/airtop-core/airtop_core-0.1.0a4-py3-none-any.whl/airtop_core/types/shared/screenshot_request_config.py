# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .screenshot_config import ScreenshotConfig

__all__ = ["ScreenshotRequestConfig"]


class ScreenshotRequestConfig(BaseModel):
    screenshot: Optional[ScreenshotConfig] = None
    """Optional configuration for the screenshot."""

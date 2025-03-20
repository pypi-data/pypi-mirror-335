# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .visual_analysis_config import VisualAnalysisConfig
from .browser_wait_navigation_config import BrowserWaitNavigationConfig

__all__ = ["MicroInteractionConfig"]


class MicroInteractionConfig(BaseModel):
    visual_analysis: Optional[VisualAnalysisConfig] = FieldInfo(alias="visualAnalysis", default=None)
    """Optional configuration for visual analysis when locating specified content."""

    wait_for_navigation_config: Optional[BrowserWaitNavigationConfig] = FieldInfo(
        alias="waitForNavigationConfig", default=None
    )
    """
    Optional configuration for waiting for navigation to complete after clicking the
    element.
    """

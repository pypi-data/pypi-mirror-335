# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .visual_analysis_config import VisualAnalysisConfig
from .browser_wait_navigation_config import BrowserWaitNavigationConfig

__all__ = ["ClickConfig", "Experimental"]


class Experimental(BaseModel):
    scroll_within: Optional[str] = FieldInfo(alias="scrollWithin", default=None)
    """A natural language description of the scrollable area on the web page.

    This identifies the container or region that should be scrolled. If missing, the
    entire page will be scrolled. You can also describe a visible reference point
    inside the container. Note: This is different from elementDescription, which
    specifies the target element to interact with. The target may be located inside
    the scrollable area defined by scrollWithin.
    """


class ClickConfig(BaseModel):
    click_type: Optional[Literal["click", "doubleClick", "rightClick"]] = FieldInfo(alias="clickType", default=None)
    """The type of click to perform. Defaults to left click."""

    experimental: Optional[Experimental] = None
    """Experimental configuration options.

    These may be subject to change and are not guaranteed to be stable across
    versions.
    """

    visual_analysis: Optional[VisualAnalysisConfig] = FieldInfo(alias="visualAnalysis", default=None)
    """Optional configuration for visual analysis when locating specified content."""

    wait_for_navigation_config: Optional[BrowserWaitNavigationConfig] = FieldInfo(
        alias="waitForNavigationConfig", default=None
    )
    """
    Optional configuration for waiting for navigation to complete after clicking the
    element.
    """

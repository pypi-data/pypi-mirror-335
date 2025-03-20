# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .visual_analysis_config import VisualAnalysisConfig
from .browser_wait_navigation_config import BrowserWaitNavigationConfig

__all__ = ["ClickConfig", "Experimental"]


class Experimental(TypedDict, total=False):
    scroll_within: Annotated[str, PropertyInfo(alias="scrollWithin")]
    """A natural language description of the scrollable area on the web page.

    This identifies the container or region that should be scrolled. If missing, the
    entire page will be scrolled. You can also describe a visible reference point
    inside the container. Note: This is different from elementDescription, which
    specifies the target element to interact with. The target may be located inside
    the scrollable area defined by scrollWithin.
    """


class ClickConfig(TypedDict, total=False):
    click_type: Annotated[Literal["click", "doubleClick", "rightClick"], PropertyInfo(alias="clickType")]
    """The type of click to perform. Defaults to left click."""

    experimental: Experimental
    """Experimental configuration options.

    These may be subject to change and are not guaranteed to be stable across
    versions.
    """

    visual_analysis: Annotated[VisualAnalysisConfig, PropertyInfo(alias="visualAnalysis")]
    """Optional configuration for visual analysis when locating specified content."""

    wait_for_navigation_config: Annotated[BrowserWaitNavigationConfig, PropertyInfo(alias="waitForNavigationConfig")]
    """
    Optional configuration for waiting for navigation to complete after clicking the
    element.
    """

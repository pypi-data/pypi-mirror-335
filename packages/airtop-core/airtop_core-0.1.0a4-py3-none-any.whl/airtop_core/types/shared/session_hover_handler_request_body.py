# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .visual_analysis_config import VisualAnalysisConfig
from .browser_wait_navigation_config import BrowserWaitNavigationConfig

__all__ = ["SessionHoverHandlerRequestBody", "Configuration", "ConfigurationExperimental"]


class ConfigurationExperimental(BaseModel):
    scroll_within: Optional[str] = FieldInfo(alias="scrollWithin", default=None)
    """A natural language description of the scrollable area on the web page.

    This identifies the container or region that should be scrolled. If missing, the
    entire page will be scrolled. You can also describe a visible reference point
    inside the container. Note: This is different from elementDescription, which
    specifies the target element to interact with. The target may be located inside
    the scrollable area defined by scrollWithin.
    """


class Configuration(BaseModel):
    experimental: Optional[ConfigurationExperimental] = None
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


class SessionHoverHandlerRequestBody(BaseModel):
    element_description: str = FieldInfo(alias="elementDescription")
    """A natural language description of where to hover (e.g.

    'the search box', 'username field'). The interaction will be aborted if the
    target element cannot be found.
    """

    client_request_id: Optional[str] = FieldInfo(alias="clientRequestId", default=None)

    configuration: Optional[Configuration] = None
    """Request configuration"""

    cost_threshold_credits: Optional[int] = FieldInfo(alias="costThresholdCredits", default=None)
    """A credit threshold that, once exceeded, will cause the operation to be
    cancelled.

    Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).
    """

    time_threshold_seconds: Optional[int] = FieldInfo(alias="timeThresholdSeconds", default=None)
    """
    A time threshold in seconds that, once exceeded, will cause the operation to be
    cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).

    This setting does not extend the maximum session duration provided at the time
    of session creation.
    """

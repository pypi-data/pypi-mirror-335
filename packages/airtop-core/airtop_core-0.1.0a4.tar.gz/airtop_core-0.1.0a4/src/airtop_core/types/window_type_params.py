# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .shared_params.visual_analysis_config import VisualAnalysisConfig
from .shared_params.browser_wait_navigation_config import BrowserWaitNavigationConfig

__all__ = ["WindowTypeParams", "Configuration", "ConfigurationExperimental"]


class WindowTypeParams(TypedDict, total=False):
    session_id: Required[Annotated[str, PropertyInfo(alias="sessionId")]]
    """The session id for the window."""

    text: Required[str]
    """The text to type into the browser window."""

    clear_input_field: Annotated[bool, PropertyInfo(alias="clearInputField")]
    """
    If true, and an HTML input field is active, clears the input field before typing
    the text.
    """

    client_request_id: Annotated[str, PropertyInfo(alias="clientRequestId")]

    configuration: Configuration
    """Request configuration"""

    cost_threshold_credits: Annotated[int, PropertyInfo(alias="costThresholdCredits")]
    """A credit threshold that, once exceeded, will cause the operation to be
    cancelled.

    Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).
    """

    element_description: Annotated[str, PropertyInfo(alias="elementDescription")]
    """A natural language description of where to type (e.g.

    'the search box', 'username field'). The interaction will be aborted if the
    target element cannot be found.
    """

    press_enter_key: Annotated[bool, PropertyInfo(alias="pressEnterKey")]
    """If true, simulates pressing the Enter key after typing the text."""

    press_tab_key: Annotated[bool, PropertyInfo(alias="pressTabKey")]
    """If true, simulates pressing the Tab key after typing the text.

    Note that the tab key will be pressed after the Enter key if both options are
    configured.
    """

    time_threshold_seconds: Annotated[int, PropertyInfo(alias="timeThresholdSeconds")]
    """
    A time threshold in seconds that, once exceeded, will cause the operation to be
    cancelled. Note that this is _not_ a hard limit, but a threshold that is checked
    periodically during the course of fulfilling the request. A default threshold is
    used if not specified, but you can use this option to increase or decrease as
    needed. Set to 0 to disable this feature entirely (not recommended).

    This setting does not extend the maximum session duration provided at the time
    of session creation.
    """

    wait_for_navigation: Annotated[bool, PropertyInfo(alias="waitForNavigation")]
    """
    If true, Airtop AI will wait for the navigation to complete after clicking the
    element.
    """


class ConfigurationExperimental(TypedDict, total=False):
    scroll_within: Annotated[str, PropertyInfo(alias="scrollWithin")]
    """A natural language description of the scrollable area on the web page.

    This identifies the container or region that should be scrolled. If missing, the
    entire page will be scrolled. You can also describe a visible reference point
    inside the container. Note: This is different from elementDescription, which
    specifies the target element to interact with. The target may be located inside
    the scrollable area defined by scrollWithin.
    """


class Configuration(TypedDict, total=False):
    experimental: ConfigurationExperimental
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

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo
from .interval_monitor_config import IntervalMonitorConfig

__all__ = ["MonitorConfig"]


class MonitorConfig(TypedDict, total=False):
    include_visual_analysis: Annotated[
        Literal["auto", "disabled", "enabled"], PropertyInfo(alias="includeVisualAnalysis")
    ]
    """
    If set to 'enabled', Airtop AI will also analyze the web page visually when
    executing the condition check. If set to 'disabled', no visual analysis will be
    conducted.
    """

    interval: IntervalMonitorConfig
    """Configuration for the interval monitor."""

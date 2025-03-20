# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["SummaryExperimentalConfig"]


class SummaryExperimentalConfig(TypedDict, total=False):
    include_visual_analysis: Annotated[str, PropertyInfo(alias="includeVisualAnalysis")]
    """
    If set to 'enabled', Airtop AI will also analyze the web page visually when
    fulfilling the request. Note that this can add to both the execution time and
    cost of the operation. If the page is too large, the context window can be
    exceeded and the request will fail. If set to 'auto' or 'disabled', no visual
    analysis will be conducted.
    """

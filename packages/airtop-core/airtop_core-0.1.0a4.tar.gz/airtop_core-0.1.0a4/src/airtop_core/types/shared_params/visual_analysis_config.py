# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["VisualAnalysisConfig"]


class VisualAnalysisConfig(TypedDict, total=False):
    max_scan_scrolls: Annotated[int, PropertyInfo(alias="maxScanScrolls")]
    """Scan mode only: The maximum number of scrolls to perform. Defaults to 50."""

    overlap_percentage: Annotated[int, PropertyInfo(alias="overlapPercentage")]
    """The percentage of overlap between screenshot chunks. Defaults to 30 (percent)."""

    partition_direction: Annotated[
        Literal["vertical", "horizontal", "bidirectional"], PropertyInfo(alias="partitionDirection")
    ]
    """
    The direction to partition the screenshot into chunks: 'vertical', 'horizontal',
    or 'bidirectional'. Defaults to 'vertical', which is recommended for most web
    pages. For optimal results when partitioning in a single direction, ensure the
    perpendicular dimension does not exceed 1920 pixels.
    """

    result_selection_strategy: Annotated[
        Literal["first", "bestMatch", "auto"], PropertyInfo(alias="resultSelectionStrategy")
    ]
    """[Experimental] The strategy to use for selecting the match using visual
    analysis.

    Can be 'auto', 'first' or 'bestMatch'. Defaults to 'auto'. Use 'auto' to let the
    system decide the best strategy. Use 'first' to select the first visual element
    that matches the element description. This will favor results that appear higher
    on the page in the event of multiple matches. Use 'bestMatch' to analyze the
    complete page and apply judgement to select the best candidate from all
    potential matches.
    """

    scan_scroll_delay: Annotated[int, PropertyInfo(alias="scanScrollDelay")]
    """Scan mode only: The delay between scrolls in milliseconds.

    Defaults to 1000 (milliseconds).
    """

    scope: Literal["viewport", "page", "scan", "auto"]
    """Whether to analyze the current viewport or the whole page.

    Can be 'viewport', 'page', 'scan' or 'auto'. Defaults to 'auto', which provides
    the simplest out-of-the-box experience for most web pages. Use 'viewport' for
    analysis of the current browser view only. Use 'page' for a full page analysis.
    Use 'scan' for a full page analysis on sites that have compatibility or accuracy
    issues with 'page' mode.
    """

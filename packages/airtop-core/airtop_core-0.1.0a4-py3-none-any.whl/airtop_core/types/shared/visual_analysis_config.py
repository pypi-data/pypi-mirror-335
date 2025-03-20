# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["VisualAnalysisConfig"]


class VisualAnalysisConfig(BaseModel):
    max_scan_scrolls: Optional[int] = FieldInfo(alias="maxScanScrolls", default=None)
    """Scan mode only: The maximum number of scrolls to perform. Defaults to 50."""

    overlap_percentage: Optional[int] = FieldInfo(alias="overlapPercentage", default=None)
    """The percentage of overlap between screenshot chunks. Defaults to 30 (percent)."""

    partition_direction: Optional[Literal["vertical", "horizontal", "bidirectional"]] = FieldInfo(
        alias="partitionDirection", default=None
    )
    """
    The direction to partition the screenshot into chunks: 'vertical', 'horizontal',
    or 'bidirectional'. Defaults to 'vertical', which is recommended for most web
    pages. For optimal results when partitioning in a single direction, ensure the
    perpendicular dimension does not exceed 1920 pixels.
    """

    result_selection_strategy: Optional[Literal["first", "bestMatch", "auto"]] = FieldInfo(
        alias="resultSelectionStrategy", default=None
    )
    """[Experimental] The strategy to use for selecting the match using visual
    analysis.

    Can be 'auto', 'first' or 'bestMatch'. Defaults to 'auto'. Use 'auto' to let the
    system decide the best strategy. Use 'first' to select the first visual element
    that matches the element description. This will favor results that appear higher
    on the page in the event of multiple matches. Use 'bestMatch' to analyze the
    complete page and apply judgement to select the best candidate from all
    potential matches.
    """

    scan_scroll_delay: Optional[int] = FieldInfo(alias="scanScrollDelay", default=None)
    """Scan mode only: The delay between scrolls in milliseconds.

    Defaults to 1000 (milliseconds).
    """

    scope: Optional[Literal["viewport", "page", "scan", "auto"]] = None
    """Whether to analyze the current viewport or the whole page.

    Can be 'viewport', 'page', 'scan' or 'auto'. Defaults to 'auto', which provides
    the simplest out-of-the-box experience for most web pages. Use 'viewport' for
    analysis of the current browser view only. Use 'page' for a full page analysis.
    Use 'scan' for a full page analysis on sites that have compatibility or accuracy
    issues with 'page' mode.
    """

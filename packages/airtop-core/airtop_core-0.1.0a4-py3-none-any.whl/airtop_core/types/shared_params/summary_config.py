# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .summary_experimental_config import SummaryExperimentalConfig

__all__ = ["SummaryConfig"]


class SummaryConfig(TypedDict, total=False):
    experimental: SummaryExperimentalConfig

    output_schema: Annotated[str, PropertyInfo(alias="outputSchema")]
    """JSON schema defining the structure of the output.

    If not provided, the format of the output might vary.
    """

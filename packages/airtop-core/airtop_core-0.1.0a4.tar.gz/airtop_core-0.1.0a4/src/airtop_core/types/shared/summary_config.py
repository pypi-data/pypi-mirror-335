# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel
from .summary_experimental_config import SummaryExperimentalConfig

__all__ = ["SummaryConfig"]


class SummaryConfig(BaseModel):
    experimental: Optional[SummaryExperimentalConfig] = None

    output_schema: Optional[str] = FieldInfo(alias="outputSchema", default=None)
    """JSON schema defining the structure of the output.

    If not provided, the format of the output might vary.
    """

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .issue import Issue
from ..._models import BaseModel

__all__ = ["AsyncSessionAIResponseEnvelope"]


class AsyncSessionAIResponseEnvelope(BaseModel):
    errors: Optional[List[Issue]] = None

    request_id: str = FieldInfo(alias="requestId")

    warnings: Optional[List[Issue]] = None

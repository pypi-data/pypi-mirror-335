# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .issue import Issue
from ..._models import BaseModel
from .envelope_default_meta import EnvelopeDefaultMeta
from .sessions_with_pagination import SessionsWithPagination

__all__ = ["SessionsResponse"]


class SessionsResponse(BaseModel):
    data: SessionsWithPagination

    errors: Optional[List[Issue]] = None

    meta: EnvelopeDefaultMeta

    warnings: Optional[List[Issue]] = None

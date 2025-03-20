# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .issue import Issue
from ..._models import BaseModel
from .envelope_default_meta import EnvelopeDefaultMeta
from .external_session_with_connection_info import ExternalSessionWithConnectionInfo

__all__ = ["SessionResponse"]


class SessionResponse(BaseModel):
    data: ExternalSessionWithConnectionInfo

    errors: Optional[List[Issue]] = None

    meta: EnvelopeDefaultMeta

    warnings: Optional[List[Issue]] = None

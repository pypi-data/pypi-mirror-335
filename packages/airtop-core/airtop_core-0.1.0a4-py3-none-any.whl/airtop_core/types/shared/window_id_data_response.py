# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .issue import Issue
from ..._models import BaseModel
from .window_id_data import WindowIDData
from .envelope_default_meta import EnvelopeDefaultMeta

__all__ = ["WindowIDDataResponse"]


class WindowIDDataResponse(BaseModel):
    data: WindowIDData

    errors: Optional[List[Issue]] = None

    meta: EnvelopeDefaultMeta

    warnings: Optional[List[Issue]] = None

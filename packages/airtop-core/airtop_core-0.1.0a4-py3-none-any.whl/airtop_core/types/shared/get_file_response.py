# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .issue import Issue
from ..._models import BaseModel
from .get_file_data import GetFileData
from .envelope_default_meta import EnvelopeDefaultMeta

__all__ = ["GetFileResponse"]


class GetFileResponse(BaseModel):
    data: GetFileData

    errors: Optional[List[Issue]] = None

    meta: EnvelopeDefaultMeta

    warnings: Optional[List[Issue]] = None

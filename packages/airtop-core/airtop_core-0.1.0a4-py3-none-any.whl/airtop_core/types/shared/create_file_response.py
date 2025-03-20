# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .issue import Issue
from ..._models import BaseModel
from .create_file_data import CreateFileData
from .envelope_default_meta import EnvelopeDefaultMeta

__all__ = ["CreateFileResponse"]


class CreateFileResponse(BaseModel):
    data: CreateFileData

    errors: Optional[List[Issue]] = None

    meta: EnvelopeDefaultMeta

    warnings: Optional[List[Issue]] = None

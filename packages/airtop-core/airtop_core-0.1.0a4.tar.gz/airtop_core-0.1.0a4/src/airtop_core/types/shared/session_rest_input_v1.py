# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .session_config_v1 import SessionConfigV1

__all__ = ["SessionRestInputV1"]


class SessionRestInputV1(BaseModel):
    configuration: Optional[SessionConfigV1] = None
    """Session configuration"""

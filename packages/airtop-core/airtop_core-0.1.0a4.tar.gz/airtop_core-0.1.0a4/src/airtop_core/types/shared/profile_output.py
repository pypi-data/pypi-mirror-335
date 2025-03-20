# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ProfileOutput"]


class ProfileOutput(BaseModel):
    created_at: Optional[datetime] = FieldInfo(alias="createdAt", default=None)
    """The date and time the profile was created. Might be null for old profiles"""

    name: str
    """Name of the profile."""

    updated_at: Optional[datetime] = FieldInfo(alias="updatedAt", default=None)
    """The date and time the profile was last updated.

    Might be null for profiles not updated recently
    """

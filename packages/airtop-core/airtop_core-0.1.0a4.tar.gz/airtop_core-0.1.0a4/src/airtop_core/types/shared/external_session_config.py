# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ExternalSessionConfig"]


class ExternalSessionConfig(BaseModel):
    base_profile_id: Optional[str] = FieldInfo(alias="baseProfileId", default=None)
    """Id of a profile to load into the session."""

    persist_profile: Optional[bool] = FieldInfo(alias="persistProfile", default=None)
    """Persist the profile."""

    timeout_minutes: Optional[int] = FieldInfo(alias="timeoutMinutes", default=None)
    """
    Max length of session in minutes, after which it will terminate if not already
    deleted.
    """

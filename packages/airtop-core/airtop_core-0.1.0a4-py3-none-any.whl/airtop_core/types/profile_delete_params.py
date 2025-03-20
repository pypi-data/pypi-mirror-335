# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ProfileDeleteParams"]


class ProfileDeleteParams(TypedDict, total=False):
    profile_ids: Annotated[Optional[List[str]], PropertyInfo(alias="profileIds")]
    """DEPRECATED. Use profileNames."""

    profile_names: Annotated[Optional[List[str]], PropertyInfo(alias="profileNames")]
    """A comma-separated list of profile names."""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ProfileRenameParams"]


class ProfileRenameParams(TypedDict, total=False):
    source: Required[str]
    """name of the profile to rename"""

    target: Required[str]
    """new name of the profile"""

    force: bool
    """Overwrite if newProfile exists.

    If not set, the operation will fail if newProfile already exists
    """

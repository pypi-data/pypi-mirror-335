# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ProfileRenameRequest"]


class ProfileRenameRequest(BaseModel):
    source: str
    """name of the profile to rename"""

    target: str
    """new name of the profile"""

    force: Optional[bool] = None
    """Overwrite if newProfile exists.

    If not set, the operation will fail if newProfile already exists
    """

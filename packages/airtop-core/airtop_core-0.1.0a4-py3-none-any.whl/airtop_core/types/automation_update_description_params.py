# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AutomationUpdateDescriptionParams"]


class AutomationUpdateDescriptionParams(TypedDict, total=False):
    id: Required[str]
    """ID of the automation to update"""

    description: Required[str]
    """New description for the automation"""

    org_id: Required[Annotated[str, PropertyInfo(alias="orgId")]]
    """Organization ID"""

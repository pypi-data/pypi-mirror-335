# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["UpdateAutomationDescriptionRequest"]


class UpdateAutomationDescriptionRequest(BaseModel):
    id: str
    """ID of the automation to update"""

    description: str
    """New description for the automation"""

    org_id: str = FieldInfo(alias="orgId")
    """Organization ID"""

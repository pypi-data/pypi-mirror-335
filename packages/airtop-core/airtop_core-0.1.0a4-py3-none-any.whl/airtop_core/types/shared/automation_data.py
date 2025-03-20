# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["AutomationData"]


class AutomationData(BaseModel):
    id: str

    domain_name: str = FieldInfo(alias="domainName")

    description: Optional[str] = None

    schema_: Optional[str] = FieldInfo(alias="schema", default=None)

    template: Optional[str] = None

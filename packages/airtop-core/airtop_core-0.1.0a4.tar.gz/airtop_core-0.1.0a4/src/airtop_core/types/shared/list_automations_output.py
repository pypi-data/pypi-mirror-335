# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .automation_data import AutomationData

__all__ = ["ListAutomationsOutput"]


class ListAutomationsOutput(BaseModel):
    automations: Optional[List[AutomationData]] = None

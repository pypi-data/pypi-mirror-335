# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["FutureGetTradingCalendarResponse"]


class FutureGetTradingCalendarResponse(BaseModel):
    data: List[str]

    success: Literal[True]

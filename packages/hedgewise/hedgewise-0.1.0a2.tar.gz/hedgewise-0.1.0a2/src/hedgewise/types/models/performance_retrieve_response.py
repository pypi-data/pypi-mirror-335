# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["PerformanceRetrieveResponse", "Data"]


class Data(BaseModel):
    horizon: int

    metric: str

    value: float

    date: Optional[str] = None


class PerformanceRetrieveResponse(BaseModel):
    data: List[Data]

    success: Literal[True]

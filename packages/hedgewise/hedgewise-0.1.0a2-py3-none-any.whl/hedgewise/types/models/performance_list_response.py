# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["PerformanceListResponse", "Data"]


class Data(BaseModel):
    description: str

    metric: str


class PerformanceListResponse(BaseModel):
    data: List[Data]

    success: Literal[True]

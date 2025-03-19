# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["SupplyListResponse", "Data"]


class Data(BaseModel):
    commodity: str

    countries: List[str]

    model: str

    symbol: str


class SupplyListResponse(BaseModel):
    data: List[Data]

    success: Literal[True]

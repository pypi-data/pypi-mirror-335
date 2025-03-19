# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .asset import Asset
from ...._models import BaseModel

__all__ = ["IndicatorListResponse", "Data"]


class Data(BaseModel):
    assets: List[Asset]

    name: str


class IndicatorListResponse(BaseModel):
    data: List[Data]

    success: Literal[True]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["FutureListResponse", "Data"]


class Data(BaseModel):
    asset_class_symbol: str

    code: Optional[str] = None

    has_forecast: bool

    name: str

    price_file: Optional[str] = None

    sku: Optional[str] = None

    symbol: str

    type: str

    exchange: Optional[str] = None

    market_date: Optional[datetime] = None

    tick_size: Optional[float] = None

    unit: Optional[str] = None


class FutureListResponse(BaseModel):
    data: List[Data]

    success: Literal[True]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import date, datetime
from typing_extensions import Literal

from ..tick import Tick
from ..._models import BaseModel
from .futures.asset import Asset

__all__ = ["FutureGetHistoricalPricesResponse", "Data", "DataContract"]


class DataContract(BaseModel):
    asset_symbol: str

    name: str

    symbol: str

    ticks: List[Tick]

    last_tick: Optional[Tick] = None

    rollover_date: Optional[date] = None


class Data(BaseModel):
    asset: Asset

    contracts: List[DataContract]

    front_month: str

    market_date: Optional[datetime] = None


class FutureGetHistoricalPricesResponse(BaseModel):
    data: Data

    success: Literal[True]

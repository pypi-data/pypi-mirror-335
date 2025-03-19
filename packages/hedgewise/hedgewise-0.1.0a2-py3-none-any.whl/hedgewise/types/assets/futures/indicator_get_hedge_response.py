# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .asset import Asset
from ...tick import Tick
from ...._models import BaseModel

__all__ = ["IndicatorGetHedgeResponse", "Data", "DataContract", "DataContractIndicator", "DataContractIndicatorSery"]


class DataContractIndicatorSery(BaseModel):
    date: str

    value: float


class DataContractIndicator(BaseModel):
    name: str

    series: List[DataContractIndicatorSery]


class DataContract(BaseModel):
    asset_symbol: str

    indicator: DataContractIndicator

    name: str

    symbol: str

    last_tick: Optional[Tick] = None


class Data(BaseModel):
    asset: Asset

    contracts: List[DataContract]


class IndicatorGetHedgeResponse(BaseModel):
    data: Data

    success: Literal[True]

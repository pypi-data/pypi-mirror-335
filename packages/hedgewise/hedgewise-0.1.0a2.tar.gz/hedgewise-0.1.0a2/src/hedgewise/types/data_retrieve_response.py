# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .tick import Tick
from .._models import BaseModel
from .assets.futures.asset import Asset

__all__ = ["DataRetrieveResponse", "Data", "DataAssetClass", "DataContract"]


class DataAssetClass(BaseModel):
    name: str

    symbol: str


class DataContract(BaseModel):
    asset_symbol: str

    name: str

    symbol: str

    last_tick: Optional[Tick] = None


class Data(BaseModel):
    asset_classes: List[DataAssetClass]

    assets: List[Asset]

    contracts: List[DataContract]


class DataRetrieveResponse(BaseModel):
    data: Data

    success: Literal[True]

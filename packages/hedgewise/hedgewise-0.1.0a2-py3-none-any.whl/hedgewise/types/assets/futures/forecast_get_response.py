# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .asset import Asset
from ...tick import Tick
from ...._models import BaseModel
from ...feature_category import FeatureCategory

__all__ = [
    "ForecastGetResponse",
    "Data",
    "DataContract",
    "DataContractForecast",
    "DataContractForecastClosePriceTrajectory",
    "DataContractMarketDriver",
    "DataContractMovingAverage",
    "DataContractMovingAverageMovingAverage",
]


class DataContractForecastClosePriceTrajectory(BaseModel):
    close_price: float

    date: datetime

    interpolated: Optional[bool] = None

    lower_bound_1_sigma: Optional[float] = None

    lower_bound_2_sigma: Optional[float] = None

    lower_bound_3_sigma: Optional[float] = None

    upper_bound_1_sigma: Optional[float] = None

    upper_bound_2_sigma: Optional[float] = None

    upper_bound_3_sigma: Optional[float] = None


class DataContractForecast(BaseModel):
    close_price_trajectory: List[DataContractForecastClosePriceTrajectory]

    forecast_date: datetime

    model: str


class DataContractMarketDriver(BaseModel):
    categories: List[FeatureCategory]

    forecast_date: datetime

    horizon: int

    model: str


class DataContractMovingAverageMovingAverage(BaseModel):
    date: datetime

    value: float


class DataContractMovingAverage(BaseModel):
    horizon: int

    moving_average: List[DataContractMovingAverageMovingAverage]


class DataContract(BaseModel):
    asset_symbol: str

    forecasts: List[DataContractForecast]

    market_drivers: Optional[List[DataContractMarketDriver]] = None

    moving_averages: Optional[List[DataContractMovingAverage]] = None

    name: str

    symbol: str

    last_tick: Optional[Tick] = None


class Data(BaseModel):
    asset: Asset

    contracts: List[DataContract]


class ForecastGetResponse(BaseModel):
    data: Data

    success: Literal[True]

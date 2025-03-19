# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import datetime
from typing import List
from typing_extensions import Literal

from .asset import Asset
from ...._models import BaseModel

__all__ = ["ForecastGetLongTermResponse", "Data", "DataLongTermForecast"]


class DataLongTermForecast(BaseModel):
    contract: str

    date: datetime.date

    price_increase: bool


class Data(BaseModel):
    asset: Asset

    long_term_forecast: List[DataLongTermForecast]


class ForecastGetLongTermResponse(BaseModel):
    data: Data

    success: Literal[True]

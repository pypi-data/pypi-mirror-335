# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .feature_category import FeatureCategory

__all__ = ["SupplyRetrieveResponse", "Data"]


class Data(BaseModel):
    commodity: str

    country: str

    country_code: str

    date: datetime

    feature_contributions: Optional[List[FeatureCategory]] = None

    forecasted_supply: float

    model: str

    reported_supply: float

    reporting_agency: str

    symbol: str

    unit: str


class SupplyRetrieveResponse(BaseModel):
    data: List[Data]

    success: Literal[True]

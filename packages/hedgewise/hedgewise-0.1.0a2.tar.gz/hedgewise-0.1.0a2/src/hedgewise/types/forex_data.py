# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from .._models import BaseModel

__all__ = ["ForexData", "Price"]


class Price(BaseModel):
    date: datetime

    price: float


class ForexData(BaseModel):
    code: str

    market_date: datetime

    name: str

    prices: List[Price]

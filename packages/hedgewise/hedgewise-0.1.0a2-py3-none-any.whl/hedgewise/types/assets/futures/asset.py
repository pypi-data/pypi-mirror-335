# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from ...._models import BaseModel

__all__ = ["Asset"]


class Asset(BaseModel):
    asset_class_symbol: str

    code: Optional[str] = None

    name: str

    price_file: Optional[str] = None

    sku: Optional[str] = None

    symbol: str

    type: str

    exchange: Optional[str] = None

    market_date: Optional[datetime] = None

    tick_size: Optional[float] = None

    unit: Optional[str] = None

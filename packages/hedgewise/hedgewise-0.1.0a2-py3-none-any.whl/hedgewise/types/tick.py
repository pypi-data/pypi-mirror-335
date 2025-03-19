# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import datetime as _datetime
from typing import Optional

from .._models import BaseModel

__all__ = ["Tick"]


class Tick(BaseModel):
    datetime: _datetime.datetime

    open_interest: int

    volume: int

    change: Optional[float] = None

    close: Optional[float] = None

    high: Optional[float] = None

    low: Optional[float] = None

    open: Optional[float] = None

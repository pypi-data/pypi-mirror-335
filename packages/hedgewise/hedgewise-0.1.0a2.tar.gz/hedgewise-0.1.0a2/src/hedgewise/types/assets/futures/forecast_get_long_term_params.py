# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["ForecastGetLongTermParams"]


class ForecastGetLongTermParams(TypedDict, total=False):
    end_date: Optional[str]
    """End of forecast window (YYYY-MM-DD).

    The returned object will contain every forecast made between start*date and
    end_date. \\__Default value* : most recent date with forecasts
    """

    horizon: Optional[int]
    """Number of months to forecast.

    _Default value_ : Shortest available term for requested symbol.
    """

    rollover_type: Optional[str]
    """Which rollover method to use. _Default value_ : hist_vol"""

    start_date: Optional[str]
    """Start of forecast window (YYYY-MM-DD).

    The returned object will contain every forecast made between start*date and
    end_date. \\__Default value* : most recent date with forecasts
    """

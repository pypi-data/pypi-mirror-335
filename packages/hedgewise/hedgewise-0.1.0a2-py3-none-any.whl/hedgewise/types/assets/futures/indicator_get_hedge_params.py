# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["IndicatorGetHedgeParams"]


class IndicatorGetHedgeParams(TypedDict, total=False):
    contract: Optional[str]
    """Contract year and month. _Default value_ : All available contracts"""

    end_date: Optional[str]
    """End of indicator window (YYYY-MM-DD).

    The returned object will contain every requested indicator made between
    start*date and end_date. \\__Default value* : most recent date with indicators
    """

    hedge_horizon: Optional[int]
    """Number of trading days in the future to hedge. _Default value_ : Full forecast"""

    lookback_days: int
    """
    Number of trading days to look back when computing indicator quintiles. _Default
    value_ : 30 days
    """

    start_date: Optional[str]
    """Start of indicator window (YYYY-MM-DD).

    The returned object will contain every requested indicator made between
    start*date and end_date. \\__Default value* : most recent date with indicators
    """

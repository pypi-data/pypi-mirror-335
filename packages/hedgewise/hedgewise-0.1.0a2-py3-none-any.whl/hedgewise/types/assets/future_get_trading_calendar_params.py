# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["FutureGetTradingCalendarParams"]


class FutureGetTradingCalendarParams(TypedDict, total=False):
    end_date: Optional[str]
    """End of trading calendar window (YYYY-MM-DD)"""

    start_date: Optional[str]
    """Start of trading calendar window (YYYY-MM-DD)"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["ForexRetrieveParams"]


class ForexRetrieveParams(TypedDict, total=False):
    end_date: Optional[str]
    """End of forex data window (YYYY-MM-DD)"""

    foreign_per_usd: bool
    """Return prices as foreign currency per USD.

    If false, prices will be returned as USD per foreign currency.
    """

    start_date: Optional[str]
    """Start of forex data window (YYYY-MM-DD)"""

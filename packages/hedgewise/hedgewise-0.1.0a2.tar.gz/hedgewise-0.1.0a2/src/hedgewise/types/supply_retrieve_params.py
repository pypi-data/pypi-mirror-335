# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["SupplyRetrieveParams"]


class SupplyRetrieveParams(TypedDict, total=False):
    country_code: Optional[str]
    """Country code (UN/LOCODE). If blank, return global data."""

    end_date: Optional[str]
    """End of date range for supply forecasts (YYYY-MM-DD)"""

    get_feature_contributions: bool
    """Return feature contributions for requested forecasts."""

    model: str
    """Supply model to use for forecasting."""

    start_date: Optional[str]
    """Start of date range for supply forecasts (YYYY-MM-DD)"""

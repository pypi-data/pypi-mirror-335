# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["ForecastGetParams"]


class ForecastGetParams(TypedDict, total=False):
    end_date: Optional[str]
    """End of forecast window (YYYY-MM-DD).

    The returned object will contain every forecast made between start*date and
    end_date. \\__Default value* : most recent date with forecasts
    """

    estimate_uncertainty: bool
    """Estimate prediction uncertainty based on recent historical accuracy."""

    get_market_drivers: bool
    """Return market drivers for each forecast."""

    get_moving_averages: bool
    """Return moving averages for each forecast."""

    interpolate: bool
    """Interpolate between forecast horizons and return daily forecast."""

    price_collar_sigma: float
    """Apply an empirical price collar to the forecasts.

    This regulates the forecast when it suggests implausibly large price changes. A
    smaller number results in a more aggressive collar. Must be a positive number.
    """

    start_date: Optional[str]
    """Start of forecast window (YYYY-MM-DD).

    The returned object will contain every forecast made between start*date and
    end_date. \\__Default value* : most recent date with forecasts
    """

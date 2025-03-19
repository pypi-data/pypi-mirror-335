# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["PerformanceRetrieveParams"]


class PerformanceRetrieveParams(TypedDict, total=False):
    end_date: Optional[str]
    """End of the performance assessment window (YYYY-MM-DD)"""

    horizon: Optional[int]
    """the horizon (number of business days in the future) of the model of interest.

    Default, returns for all horizons
    """

    metric: Optional[str]
    """the requested metric as described in the metadata. Default: hitrate"""

    sigma: float
    """Number of standard deviations to calculate for ACE. Unused for other metrics."""

    start_date: Optional[str]
    """Start of the performance assessment window (YYYY-MM-DD)"""

    threshold_on_actual: Optional[float]
    """
    Allows to assess directional performance filtered on days where the % realized
    price change is greater than threshold. Default: no filter. Valid only for
    hitrate style metrics. Eg. enter 0.02 for 2%
    """

    threshold_on_forecast: Optional[float]
    """
    Allows to assess directional performance filtered on days where the % expected
    change of the forecast is greater than threshold. Default: no filter. Valid only
    for hitrate style metrics. Eg. enter 0.02 for 2%
    """

    use_run_date: bool
    """Use the run date of the forecast to filter the performance assessment window.

    If false, use the target date. Setting this to false makes the result
    deterministic from day to day.
    """

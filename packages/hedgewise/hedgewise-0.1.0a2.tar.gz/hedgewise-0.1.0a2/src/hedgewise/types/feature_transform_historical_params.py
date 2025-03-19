# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["FeatureTransformHistoricalParams"]


class FeatureTransformHistoricalParams(TypedDict, total=False):
    transform: Required[str]
    """The type of transform requested.

    Currently supported are `xyavg`, `rebase`, `zscore`, `yoy`
    """

    end_date: Optional[str]
    """End of transformed feature data window (YYYY-MM-DD) - not relevant for yoy"""

    number_of_years: int
    """Number of years to perform the average on. (valid for xyavg and yoy transforms)"""

    start_date: Optional[str]
    """Start of transformed feature data window (YYYY-MM-DD) - not relevant for yoy"""

    window: int
    """Number of observations used in the transformation window.

    (valid for xyavg and zscore transforms)
    """

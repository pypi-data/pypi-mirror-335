# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["FeatureRetrieveHistoricalParams"]


class FeatureRetrieveHistoricalParams(TypedDict, total=False):
    add_strength_for_commodity: Optional[str]
    """
    If a future symbol is provided and a model for that commodity exists, a signed
    strength indicator will be returned in addition to the feature value
    """

    agg: Optional[str]
    """
    If a `weekly` or `monthly` frequency is requested, this parameter allows to
    control how the returned data is aggregated over each period. `mean` and `last`
    are supported
    """

    end_date: Optional[str]
    """End of feature data window (YYYY-MM-DD)"""

    freq: Optional[str]
    """By default, time-series are returned using daily time frequency.

    Request resampled data using `weekly` or `monthly` as query parameter
    """

    start_date: Optional[str]
    """Start of feature data window (YYYY-MM-DD)"""

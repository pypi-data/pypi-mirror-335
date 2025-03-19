# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Iterable, Optional
from typing_extensions import Required, TypedDict

__all__ = ["FeatureGetWeightedIndexParams"]


class FeatureGetWeightedIndexParams(TypedDict, total=False):
    feature_codes: Required[List[str]]
    """The list of features to include in the index"""

    index_label: Required[str]
    """user defined string used to name the weighted index"""

    weights: Required[Iterable[float]]
    """The list of weights to apply on the features selection to create the index"""

    end_date: Optional[str]
    """End of transformed feature data window (YYYY-MM-DD)"""

    start_date: Optional[str]
    """Start of transformed feature data window (YYYY-MM-DD)"""

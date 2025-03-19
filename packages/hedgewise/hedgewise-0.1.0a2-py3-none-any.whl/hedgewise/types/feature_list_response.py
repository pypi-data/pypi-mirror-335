# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FeatureListResponse", "Data"]


class Data(BaseModel):
    feature_code: str

    long_name: str

    type: str

    variable_type: str

    country: Optional[str] = None

    location: Optional[str] = None

    main_commodity: Optional[str] = None

    recent_influence: Optional[float] = None

    source: Optional[str] = None

    statistic_type: Optional[str] = None

    symbols: Optional[List[str]] = None

    unit: Optional[str] = None


class FeatureListResponse(BaseModel):
    data: List[Data]

    success: Literal[True]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import datetime
from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["FeatureRetrieveHistoricalResponse", "Data"]


class Data(BaseModel):
    date: datetime.date

    feature_code: str

    value: float

    phenology_stage: Optional[str] = None

    strength: Optional[float] = None


class FeatureRetrieveHistoricalResponse(BaseModel):
    data: List[Data]

    success: Literal[True]

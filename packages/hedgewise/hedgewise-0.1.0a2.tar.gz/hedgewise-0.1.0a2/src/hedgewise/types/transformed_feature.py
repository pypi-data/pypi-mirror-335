# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import datetime
from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TransformedFeature", "Data"]


class Data(BaseModel):
    date: datetime.date

    value: float

    xform_feature_code: str

    label: Optional[str] = None


class TransformedFeature(BaseModel):
    data: List[Data]

    success: Literal[True]

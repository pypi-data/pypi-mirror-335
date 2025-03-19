# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel
from .forex_data import ForexData

__all__ = ["ForexListResponse"]


class ForexListResponse(BaseModel):
    data: List[ForexData]

    success: Literal[True]

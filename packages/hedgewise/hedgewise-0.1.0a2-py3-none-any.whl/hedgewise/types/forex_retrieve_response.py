# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel
from .forex_data import ForexData

__all__ = ["ForexRetrieveResponse"]


class ForexRetrieveResponse(BaseModel):
    data: ForexData

    success: Literal[True]

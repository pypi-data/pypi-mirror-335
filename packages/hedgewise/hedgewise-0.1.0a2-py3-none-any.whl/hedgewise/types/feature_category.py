# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["FeatureCategory", "Drilldown"]


class Drilldown(BaseModel):
    contribution: float

    description: str

    feature_code: str


class FeatureCategory(BaseModel):
    category: str

    contribution: float

    drilldown: Optional[List[Drilldown]] = None

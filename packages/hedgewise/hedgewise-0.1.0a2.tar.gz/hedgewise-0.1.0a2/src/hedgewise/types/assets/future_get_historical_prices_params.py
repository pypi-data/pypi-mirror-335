# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["FutureGetHistoricalPricesParams"]


class FutureGetHistoricalPricesParams(TypedDict, total=False):
    active_contracts_only: bool
    """Return price data for currently active contracts only.

    Set to false to also retrieve price data from expired contracts.
    """

    back_adjust: bool
    """
    Back-adjust prices to account for calendar spread at contract rollover dates.
    The method used is described here:
    https://www.sierrachart.com/index.php?page=doc/ContinuousFuturesContractCharts.html#ContinuousFuturesContractDateRuleRolloverBackAdjusted
    """

    contract: Optional[str]
    """Contract year and month. _Default value_ : All available contracts"""

    end_date: Optional[str]
    """End of prices window (YYYY-MM-DD).

    The returned object will contain the entire price history for every contract
    that traded between `start_date` and `end_date`. Ignored if `contract` is
    specified. _Default value_ : most recent date with prices
    """

    rollover_method: str
    """
    The rollover date is the most recent date for which a given contract was trading
    as the front month. This parameter specifies the method used to determine the
    rollover date for contracts. Must be one of "hist_vol", "max_vol",
    "first_notice", or "last_trade" (or left blank for no rollover calculation).
    "first_notice" not available for all commodities, and defaults to "last_trade".
    """

    start_date: Optional[str]
    """Start of prices window (YYYY-MM-DD).

    The returned object will contain the entire price history for every contract
    that traded between `start_date` and `end_date`. Ignored if `contract` is
    specified. _Default value_ : most recent date with prices
    """

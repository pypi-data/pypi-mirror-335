from typing import List
from pydantic import Field
from at_common_schemas.base import BaseSchema
from at_common_schemas.core.calendar import (
    Dividends, Earnings, Splits
)

# Earnings
class CalendarEarningsListRequest(BaseSchema):
    """Request parameters for retrieving earnings calendar data."""
    symbol: str = Field(..., description="The stock symbol for the request.")
    limit: int = Field(..., description="The number of results to return.")

class CalendarEarningsListResponse(BaseSchema):
    """Response containing earnings calendar data."""
    items: List[Earnings] = Field(..., description="List of daily earnings announcements within the requested date range")

# Dividend
class CalendarDividendsListRequest(BaseSchema):
    """Request parameters for retrieving dividend calendar data."""
    symbol: str = Field(..., description="The stock symbol for the request.")
    limit: int = Field(..., description="The number of results to return.")

class CalendarDividendsListResponse(BaseSchema):
    """Response containing dividend calendar data."""
    items: List[Dividends] = Field(..., description="List of calendar dividends.")

# Split
class CalendarSplitsListRequest(BaseSchema):
    """Request parameters for retrieving stock split calendar data."""
    symbol: str = Field(..., description="The stock symbol for the request.")
    limit: int = Field(..., description="The number of results to return.")

class CalendarSplitsListResponse(BaseSchema):
    """Response containing stock split calendar data."""
    items: List[Splits] = Field(..., description="List of daily stock splits within the requested date range")
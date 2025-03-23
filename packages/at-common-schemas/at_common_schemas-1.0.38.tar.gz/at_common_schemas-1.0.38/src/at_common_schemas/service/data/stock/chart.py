from datetime import datetime
from typing import List
from at_common_schemas.base import BaseSchema
from pydantic import Field
from at_common_schemas.core.chart import ChartEOD, ChartIntraday

# Base request classes
class ChartBaseRequest(BaseSchema):
    symbol: str = Field(..., description="Stock symbol")

class ChartDateRangeRequest(ChartBaseRequest):
    date_from: datetime = Field(..., description="Start date for the request")
    date_to: datetime = Field(..., description="End date for the request")

class ChartTimeRangeRequest(ChartBaseRequest):
    time_from: datetime = Field(..., description="Start time for the request")
    time_to: datetime = Field(..., description="End time for the request")

# EOD classes
class ChartEODListRequest(ChartDateRangeRequest):
    pass

class ChartEODListResponse(BaseSchema):
    items: List[ChartEOD] = Field(..., description="List of daily candlestick data")

class ChartIntradayListResponse(BaseSchema):
    items: List[ChartIntraday] = Field(..., description="List of intraday candlestick data")

# For backward compatibility, you can keep the specific classes
class ChartIntraday5MinuteListRequest(ChartTimeRangeRequest):
    pass

class ChartIntraday5MinuteListResponse(ChartIntradayListResponse):
    pass

class ChartIntraday15MinuteListRequest(ChartTimeRangeRequest):
    pass

class ChartIntraday15MinuteListResponse(ChartIntradayListResponse):
    pass

class ChartIntraday30MinuteListRequest(ChartTimeRangeRequest):
    pass

class ChartIntraday30MinuteListResponse(ChartIntradayListResponse):
    pass

class ChartIntraday1HourListRequest(ChartTimeRangeRequest):
    pass

class ChartIntraday1HourListResponse(ChartIntradayListResponse):
    pass

class ChartIntraday4HourListRequest(ChartTimeRangeRequest):
    pass

class ChartIntraday4HourListResponse(ChartIntradayListResponse):
    pass
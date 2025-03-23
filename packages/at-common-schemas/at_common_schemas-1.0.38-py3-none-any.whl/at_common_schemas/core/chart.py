from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime
from enum import Enum

class ChartInterval(str, Enum):
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    EOD = "eod"

class ChartEOD(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    date: datetime = Field(..., description="Date of the price data")
    open: float = Field(..., description="Opening price for the trading day")
    high: float = Field(..., description="Highest price reached during the trading day")
    low: float = Field(..., description="Lowest price reached during the trading day")
    close: float = Field(..., description="Closing price for the trading day")
    volume: int = Field(..., description="Trading volume for the day")
    change: float = Field(..., description="Absolute price change from previous day")
    change_percent: float = Field(..., description="Percentage price change from previous day")
    vwap: float = Field(..., description="Volume Weighted Average Price for the day")

class ChartEODAdjusted(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    date: datetime = Field(..., description="Date of the price data")
    adj_open: float = Field(..., description="Adjusted opening price accounting for corporate actions")
    adj_high: float = Field(..., description="Adjusted highest price accounting for corporate actions")
    adj_low: float = Field(..., description="Adjusted lowest price accounting for corporate actions")
    adj_close: float = Field(..., description="Adjusted closing price accounting for corporate actions")
    volume: int = Field(..., description="Trading volume for the day")

class ChartIntraday(BaseSchema):
    time: datetime = Field(..., description="Time of the intraday price data")
    open: float = Field(..., description="Opening price for the time interval")
    high: float = Field(..., description="Highest price during the time interval")
    low: float = Field(..., description="Lowest price during the time interval")
    close: float = Field(..., description="Closing price for the time interval")
    volume: int = Field(..., description="Trading volume for the time interval")
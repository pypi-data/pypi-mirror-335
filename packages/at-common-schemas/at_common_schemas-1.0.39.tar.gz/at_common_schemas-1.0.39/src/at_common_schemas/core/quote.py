from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class Quote(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol")
	name: str = Field(..., description="Full company or security name")
	price: float = Field(..., description="Current market price")
	change_percentage: float = Field(..., description="Percentage price change from previous close")
	change: float = Field(..., description="Absolute price change from previous close")
	volume: int = Field(..., description="Trading volume for the current session")
	day_low: float = Field(..., description="Lowest price reached during current trading day")
	day_high: float = Field(..., description="Highest price reached during current trading day")
	year_high: float = Field(..., description="Highest price reached in the past 52 weeks")
	year_low: float = Field(..., description="Lowest price reached in the past 52 weeks")
	market_cap: int = Field(..., description="Total market capitalization in base currency")
	price_avg50: float = Field(..., description="50-day moving average price")
	price_avg200: float = Field(..., description="200-day moving average price")
	exchange: str = Field(..., description="Name of the exchange where the security is traded")
	open: float = Field(..., description="Opening price for the current trading day")
	previous_close: float = Field(..., description="Closing price from the previous trading day")
	time: datetime = Field(..., description="time of the quote")

class QuoteShort(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol")
	price: float | None = Field(None, description="Current market price if available")
	change: float | None = Field(None, description="Absolute price change from previous close if available")
	volume: int | float | None = Field(None, description="Trading volume for the current session if available")

class AfterMarketTrade(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol")
	price: float = Field(..., description="Price at which the after-hours trade occurred")
	trade_size: int = Field(..., description="Number of shares in the after-hours trade")
	time: datetime = Field(..., description="time of the trade")

class AfterMarketQuote(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol")
	bid_size: int = Field(..., description="Number of shares being bid in after-hours")
	bid_price: float = Field(..., description="Highest price buyers are willing to pay in after-hours")
	ask_size: int = Field(..., description="Number of shares being offered in after-hours")
	ask_price: float = Field(..., description="Lowest price sellers are willing to accept in after-hours")
	volume: int = Field(..., description="Total after-hours trading volume")
	time: datetime = Field(..., description="time of the after-hours quote")

class PriceChange(BaseSchema):
	symbol: str = Field(..., description="Stock ticker symbol")
	one_day: float = Field(..., alias="1D", description="Percentage price change over the past day")
	five_day: float = Field(..., alias="5D", description="Percentage price change over the past 5 trading days")
	one_month: float = Field(..., alias="1M", description="Percentage price change over the past month")
	three_month: float = Field(..., alias="3M", description="Percentage price change over the past 3 months")
	ytd: float = Field(..., alias="ytd", description="Percentage price change year-to-date")
	one_year: float = Field(..., alias="1Y", description="Percentage price change over the past year")
	three_year: float = Field(..., alias="3Y", description="Percentage price change over the past 3 years")
	five_year: float = Field(..., alias="5Y", description="Percentage price change over the past 5 years")
	ten_year: float = Field(..., alias="10Y", description="Percentage price change over the past 10 years")
	max: float = Field(..., alias="max", description="Maximum percentage price change since inception")
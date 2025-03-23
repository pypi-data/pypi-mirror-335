from pydantic import Field
from at_common_schemas.base import BaseSchema

class MarketHours(BaseSchema):
    exchange: str = Field(..., description="The identifier code for the exchange")
    name: str = Field(..., description="The full name of the exchange")
    opening_hour: str = Field(..., description="The time when trading begins on the exchange")
    closing_hour: str = Field(..., description="The time when trading ends on the exchange")
    timezone: str = Field(..., description="The timezone in which the opening and closing hours are specified")
    is_market_open: bool = Field(..., description="Indicates whether the market is currently open for trading")
from pydantic import Field
from at_common_schemas.base import BaseSchema
from datetime import datetime

class CryptoCurrency(BaseSchema):
    symbol: str = Field(..., description="The ticker symbol of the cryptocurrency (e.g., BTC, ETH)")
    name: str = Field(..., description="The full name of the cryptocurrency")
    exchange: str = Field(..., description="The exchange platform where the cryptocurrency is traded")
    ico_date: datetime | None = Field(None, description="The initial coin offering date in string format, if applicable")
    circulating_supply: int | float | None = Field(None, description="The number of coins currently in circulation and publicly available")
    total_supply: int | float | None = Field(None, description="The maximum number of coins that will ever exist for this cryptocurrency")
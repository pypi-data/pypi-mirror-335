from pydantic import Field
from at_common_schemas.base import BaseSchema

class CommodityItem(BaseSchema):
    symbol: str = Field(..., description="The unique identifier code for the commodity")
    name: str = Field(..., description="The full descriptive name of the commodity")
    exchange: str | None = Field(None, description="The trading exchange where the commodity is listed, if applicable")
    trade_month: str = Field(..., description="The contract month for futures trading of the commodity")
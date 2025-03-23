from pydantic import Field
from at_common_schemas.base import BaseSchema

class Forex(BaseSchema):
    symbol: str = Field(..., description="The trading symbol representing the currency pair")
    from_currency: str = Field(..., description="The base currency code in the currency pair")
    to_currency: str = Field(..., description="The quote currency code in the currency pair")
    from_name: str = Field(..., description="The full name of the base currency")
    to_name: str = Field(..., description="The full name of the quote currency")
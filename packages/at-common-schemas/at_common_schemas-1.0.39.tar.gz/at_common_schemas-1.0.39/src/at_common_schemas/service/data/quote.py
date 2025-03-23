from pydantic import Field
from at_common_schemas.base import BaseSchema
from at_common_schemas.core.quote import Quote

# Quote
class QuoteGetRequest(BaseSchema):
    symbol: str = Field(..., description="ticker symbol")

class QuoteGetResponse(Quote):
    pass
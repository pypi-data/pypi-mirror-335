from pydantic import Field
from at_common_schemas.base import BaseSchema

class SearchResult(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Full company name")
    currency: str = Field(..., description="Trading currency code")
    exchange_full_name: str = Field(..., description="Complete name of the stock exchange")
    exchange: str = Field(..., description="Stock exchange code")

class SearchCIKResult(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Full company name")
    cik: str = Field(..., description="Central Index Key (CIK) identifier assigned by the SEC")
    exchange_full_name: str = Field(..., description="Complete name of the stock exchange")
    exchange: str = Field(..., description="Stock exchange code")
    currency: str = Field(..., description="Trading currency code")

class SearchCusipResult(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    company_name: str = Field(..., description="Full company name")
    cusip: str = Field(..., description="Committee on Uniform Securities Identification Procedures (CUSIP) identifier")
    market_cap: int = Field(..., description="Market capitalization value in the trading currency")

class SearchISINResult(BaseSchema):
    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Full company name")
    isin: str = Field(..., description="International Securities Identification Number (ISIN)")
    market_cap: int = Field(..., description="Market capitalization value in the trading currency")
    
    